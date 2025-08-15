import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from parse_youtube import get_video_id, get_youtube_data, get_youtube_transcript

load_dotenv()

# Pinecone configuration
INDEX_NAME = "youtube-videos"
EMBEDDING_DIMENSION = 384

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

def insert_videos_to_collection(index, url):
    """Insert video data with semantic embeddings into Pinecone collection"""
    try:
        # Initialize embedding model
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Get video data from URL
        video_data = get_youtube_data(url)
        video_id = video_data['video_id']
        
        # Get transcript data
        transcript = get_youtube_transcript(url)
        
        if not transcript:
            print(f"⚠️ No transcript available for video: {video_data['title']}")
            return False
        
        # Generate semantic embedding from transcript
        embedding = embedding_model.encode(transcript).tolist()
        
        # Prepare vector for Pinecone upsert
        vector = {
            "id": video_id,
            "values": embedding,
            "metadata": {
                "title": video_data['title'],
                "url": video_data['url'],
                "thumbnail": video_data['thumbnail'],
                "description": video_data['description'],
                "content": transcript[:500],  # Store first 500 chars for preview
                "full_transcript": transcript,
                "type": "youtube_transcript"
            }
        }
        
        # Upsert to Pinecone
        index.upsert(vectors=[vector])
        print(f"✅ Successfully inserted video: {video_data['title']}")
        print(f"Video ID: {video_id}")
        print(f"Embedding dimension: {len(embedding)}")
        
        return True
    except Exception as e:
        print(f"❌ Error inserting data to Pinecone: {e}")
        return False

def delete_video_from_collection(index, video_id):
    """Delete a specific video from Pinecone collection by video_id"""
    try:
        # Delete the vector with the specified video_id
        index.delete(ids=[video_id])
        print(f"✅ Successfully deleted video with ID: {video_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting video from Pinecone: {e}")
        return False

if __name__ == "__main__":
    # Test Pinecone connection and deletion
    print("🔄 Testing Pinecone connection...")
    index = connect_to_pinecone()
    
    if index:
        # Extract video ID from the provided URL
        test_url = "https://www.youtube.com/watch?v=I-GWFWc8P4Y&list=PLqMymTkulLcK_gXfkH94oNH0xLfW9W935&index=2&t=393s"
        video_id = get_video_id(test_url)
        
        if video_id:
            print(f"\n🔄 Testing video deletion for ID: {video_id}")
            delete_result = delete_video_from_collection(index, video_id)
            
            if delete_result:
                print("\n✅ Video deleted successfully from Pinecone")
            else:
                print("\n⚠️ Failed to delete video (may not exist in collection)")
        else:
            print("\n❌ Could not extract video ID from URL")
    else:
        print("❌ Could not connect to Pinecone")
    