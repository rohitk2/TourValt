import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

# Helper functions
def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed = urlparse(url)
    return parsed.path[1:] if parsed.hostname == 'youtu.be' else parse_qs(parsed.query)['v'][0]

def get_youtube_data(url):
    """Get YouTube video metadata: title, thumbnail, description"""
    video_id = get_video_id(url)
    
    try:
        response = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json")
        data = response.json() if response.status_code == 200 else {}
    except:
        data = {}
    
    return {
        'title': data.get('title', 'Unknown Title'),
        'thumbnail': data.get('thumbnail_url', f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'),
        'description': data.get('author_name', 'No description available'),
        'video_id': video_id,
        'url': url
    }

def get_youtube_transcript(url):
    """Get YouTube transcript directly (no caching)"""
    video_id = get_video_id(url)
    print(f"🔄 Fetching transcript for: {video_id}")
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = ytt_api.fetch(video_id).to_raw_data()
        transcript_text = ' '.join([entry['text'] for entry in transcript_data])
        print(f"✅ Successfully fetched transcript ({len(transcript_text)} chars)")

        # Print the transcript text for caching purposes
        print(f"\n📝 TRANSCRIPT TEXT:")
        print(f"{'='*50}")
        print(transcript_text)
        print(f"{'='*50}\n")

        return transcript_text
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return ""