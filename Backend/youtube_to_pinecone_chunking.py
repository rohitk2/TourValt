import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from parse_youtube import get_video_id, get_youtube_data, get_youtube_transcript
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

# Pinecone configuration
INDEX_NAME = "youtube-videos"
EMBEDDING_DIMENSION = 384

def chunk_transcript_data(transcript_data, max_chars, overlap=50):
    """Chunk transcript data into segments of max_chars with overlap and time intervals"""
    chunks = []
    
    # First, combine all transcript entries into one continuous text with timing info
    full_text = ""
    char_to_time = []  # Maps character position to (start_time, end_time)
    
    for entry in transcript_data:
        text = entry['text']
        start_time = entry['start']
        end_time = entry['start'] + entry['duration']
        
        # Map each character in this entry to its timing
        for _ in range(len(text)):
            char_to_time.append((start_time, end_time))
        
        full_text += text
        
        # Add space between entries and map it to the same timing
        if full_text and not full_text.endswith(' '):
            full_text += ' '
            char_to_time.append((start_time, end_time))
    
    # Now create overlapping chunks
    start_pos = 0
    
    while start_pos < len(full_text):
        # Calculate end position for this chunk
        end_pos = min(start_pos + max_chars, len(full_text))
        
        # Extract chunk text
        chunk_text = full_text[start_pos:end_pos].strip()
        
        if chunk_text:  # Only add non-empty chunks
            # Get timing for this chunk
            chunk_start_time = char_to_time[start_pos][0] if start_pos < len(char_to_time) else 0
            chunk_end_time = char_to_time[min(end_pos - 1, len(char_to_time) - 1)][1] if char_to_time else 0
            
            chunks.append({
                'text': chunk_text,
                'start': chunk_start_time,
                'end': chunk_end_time
            })
        
        # Move to next chunk position with overlap
        # If this is the last chunk, break
        if end_pos >= len(full_text):
            break
            
        # Calculate next start position (current end - overlap)
        start_pos = max(end_pos - overlap, start_pos + 1)  # Ensure we always move forward
    
    return chunks


def get_youtube_transcript_chunked(url, chunk_size=500):
    """Get YouTube transcript and chunk it into segments of specified character count"""
    video_id = get_video_id(url)
    print(f"🔄 Fetching transcript for: {video_id}")
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = ytt_api.fetch(video_id).to_raw_data()
        
        # Chunk the transcript data using character-based chunking with overlap
        chunked_data = chunk_transcript_data(transcript_data, max_chars=chunk_size, overlap=50)
        
        print(f"✅ Successfully chunked transcript into {len(chunked_data)} segments")
        print(f"{'='*50}")
        
        # Print first few chunks as examples
        for i, chunk in enumerate(chunked_data[:30]):  # Show first 3 chunks
            print(f"Chunk {i+1}:")
            print(f"  Start: {chunk['start']}, End: {chunk['end']}")
            print(f"  Character count: {len(chunk['text'])}")
            print(f"  Text preview: {chunk['text']}...")
            print()
        
        return chunked_data
        
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return []

def connect_to_pinecone():
    """Connect to Pinecone and return the index"""
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Create index if it doesn't exist
        if INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            print(f"✅ Created new Pinecone index: {INDEX_NAME}")
        
        index = pc.Index(INDEX_NAME)
        print("✅ Successfully connected to Pinecone!")
        return index
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return None

def insert_videos_to_collection(index, url, chunk_size=500):
    """Insert video data with chunked semantic embeddings into Pinecone collection"""
    try:
        # Initialize embedding model
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Get video data from URL
        video_data = get_youtube_data(url)
        video_id = video_data['video_id']
        
        # Get chunked transcript data using the chunked implementation
        chunked_transcript = get_youtube_transcript_chunked(url, chunk_size)
        
        if not chunked_transcript:
            print(f"⚠️ No transcript available for video: {video_data['title']}")
            return False
        
        vectors_to_upsert = []
        
        # Process each chunk and create separate vectors
        for i, chunk in enumerate(chunked_transcript):
            # Create combined text from title, description, and transcript chunk
            combined_text = f"{video_data['title']} {video_data['description']} {chunk['text']}"
            
            # Generate semantic embedding from combined text
            embedding = embedding_model.encode(combined_text).tolist()
            
            # Create unique ID for each chunk
            chunk_id = f"{video_id}_chunk_{i}"
            
            # Prepare vector for Pinecone upsert with new metadata structure
            vector = {
                "id": chunk_id,
                "values": embedding,  # Now contains embedding of title + description + transcript
                "metadata": {
                    "title": video_data['title'],
                    "url": video_data['url'],
                    "thumbnail": video_data['thumbnail'],
                    "content": chunk['text'],  # Keep original transcript text for display
                    "start": chunk['start'],
                    "end": chunk['end'],
                    "type": "youtube_transcript_chunk"
                }
            }
            
            vectors_to_upsert.append(vector)
        
        # Upsert all chunks to Pinecone in batch
        index.upsert(vectors=vectors_to_upsert)
        
        print(f"✅ Successfully inserted {len(vectors_to_upsert)} chunks for video: {video_data['title']}")
        print(f"Video ID: {video_id}")
        print(f"Chunks created: {len(chunked_transcript)}")
        print(f"Embedding dimension: {len(vectors_to_upsert[0]['values']) if vectors_to_upsert else 'N/A'}")
        
        return True
    except Exception as e:
        print(f"❌ Error inserting data to Pinecone: {e}")
        return False

def delete_video_from_collection(index, video_id):
    """Delete all chunks of a specific video from Pinecone collection by video_id"""
    try:
        # Since we don't have a direct way to list all IDs with a prefix,
        # we'll use the metadata filter approach
        
        # First, let's try to get all vectors and filter by video_id in chunk ID
        # This is a workaround since Pinecone doesn't support prefix deletion directly
        
        # Query with a filter on the URL metadata (which should be unique per video)
        query_response = index.query(
            vector=[0] * EMBEDDING_DIMENSION,  # Dummy vector
            filter={
                "url": {"$eq": f"https://www.youtube.com/watch?v={video_id}"}  # Exact URL match
            },
            top_k=1000,  # Should cover all chunks for a single video
            include_metadata=True
        )
        
        # Extract chunk IDs
        chunk_ids_to_delete = [match['id'] for match in query_response['matches']]
        
        if chunk_ids_to_delete:
            # Delete all chunks
            index.delete(ids=chunk_ids_to_delete)
            print(f"✅ Successfully deleted {len(chunk_ids_to_delete)} chunks for video ID: {video_id}")
        else:
            print(f"⚠️ No chunks found for video ID: {video_id}")
        
        return True
    except Exception as e:
        print(f"❌ Error deleting video chunks from Pinecone: {e}")
        return False

def semantic_search(index, text, k=3):
    """Perform semantic search using pre-computed combined embeddings (title + description + content)"""
    try:
        # Initialize embedding model (same as used for indexing)
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Generate embedding for the search query
        query_embedding = embedding_model.encode(text).tolist()
        
        # Perform the search against pre-computed combined embeddings
        search_results = index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True,
            filter={
                "type": {"$eq": "youtube_transcript_chunk"}
            }
        )
        
        # Process and return results as list of dictionaries
        results = []
        
        for match in search_results['matches']:
            result = {
                'title': match['metadata']['title'],
                'content': match['metadata']['content'],
                'thumbnail': match['metadata']['thumbnail'],
                'start': match['metadata']['start'],
                'end': match['metadata']['end'],
                'score': match['score']
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"❌ Error performing semantic search: {e}")
        return []

if __name__ == "__main__":
    index = connect_to_pinecone()
    
    if not index:
        print("❌ Failed to connect to Pinecone. Exiting.")
        exit(1)
    
    # URLs to insert into Pinecone
    test_urls = [
        'https://www.youtube.com/watch?v=A6ifN1CCv9o&list=PLr_pMIbWaVLfydOCyqqo6Zu2oB7bTCE52&index=2',
        'https://www.youtube.com/watch?v=GV2QZbMO0CM&list=PLr_pMIbWaVLfydOCyqqo6Zu2oB7bTCE52&index=3',
        'https://www.youtube.com/watch?v=m5WKOEvBh7Y&list=PLr_pMIbWaVLfydOCyqqo6Zu2oB7bTCE52&index=6'
    ]
    
    # Interactive search loop
    while True:
        # Ask if user wants to continue
        while True:
            user_input = input("\nDo you want to continue [Y/N]? ").strip().upper()
            if user_input == 'Y':
                break
            elif user_input == 'N':
                print("👋 Goodbye!")
                exit(0)
            else:
                continue  # Repeat the question
        
        # Ask for search text
        search_text = input("\nEnter a text: ").strip()
        
        if search_text:
            # Invoke the semantic_search function and store results
            search_results = semantic_search(index, search_text, k=3)
            
            # Print results in a readable format
            if search_results:
                print(f"\n{'='*80}")
                print(f"🔍 SEARCH RESULTS FOR: '{search_text}'")
                print(f"{'='*80}")
                print(f"Found {len(search_results)} matching chunks:\n")
                
                for i, result in enumerate(search_results, 1):
                    print(f"📝 CHUNK {i} (Score: {result['score']:.4f})")
                    print(f"🎬 Video: {result['title']}")
                    print(f"🖼️ Thumbnail: {result['thumbnail']}")
                    print(f"⏰ Time: {result['start']:.1f}s - {result['end']:.1f}s")
                    print(f"📄 Transcript:")
                    print(f"   {result['content']}")
                    print(f"{'-'*60}\n")
                
                print(f"✅ Completed search for query: '{search_text}'")
                print(f"{'='*80}\n")
            else:
                print("⚠️ No search results found.")
        else:
            print("⚠️ No text entered. Please try again.")
    
    

    
    