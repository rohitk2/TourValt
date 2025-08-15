from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_youtube_description(url):
    """
    Get the description of a YouTube video using its URL.
    """ 
    parsed = urlparse(url)
    video_id = parsed.path[1:] if parsed.hostname == 'youtu.be' else parse_qs(parsed.query)['v'][0]
    ytt_api = YouTubeTranscriptApi()
    transcript_data = ytt_api.fetch(video_id).to_raw_data()
    transcript_text = ' '.join([entry['text'] for entry in transcript_data])

    #print(transcript_text, end='\n\n\n\n')
    yt_title = model.generate_content(f"Can you create a Youtube title for this video PICK BEST ONE DON'T GIVE OPTIONS -- response no more than 10 words: {transcript_text}")
    yt_description = model.generate_content(f"Can you create a Youtube description for this video: {transcript_text}")
    return yt_title.text, yt_description.text

urls = [
    "https://www.youtube.com/watch?v=H323jUyctWs&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=2",
    "https://www.youtube.com/watch?v=2c-OImps6vY&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=8",
    "https://www.youtube.com/watch?v=4Ll-IHeRmiQ&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=9",
    "https://www.youtube.com/watch?v=j3Rs_STAWJQ&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=10",
    "https://www.youtube.com/watch?v=2VRFkiXwJk4&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=11",
    "https://www.youtube.com/watch?v=6Fskt54oTyE&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=12",
    "https://www.youtube.com/watch?v=-AMatpvz7PE&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=13",
    "https://www.youtube.com/watch?v=jSXdlDuJa3o&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=14",
    "https://www.youtube.com/watch?v=_f-KxpbHjRQ&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=15",
    "https://www.youtube.com/watch?v=ZaLYbkPn82E&list=PL9FTnKxZ3quDnUBDZVosIkqAnG_u9O4Yp&index=16"
]

for url in urls:
    yt_title, yt_description = get_youtube_description(url)
    title = yt_title
    description = yt_description
    
    # Create text file for this video
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title.strip())
    filename = f"{safe_title}.txt"
    os.makedirs("Playlist_Folder", exist_ok=True)
    filepath = os.path.join("Playlist_Folder", filename)
    
    content = f"""{title}.txt
------------
URL: {url}

TITLE: {title}

DESCRIPTION:
{description}
--------------"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {filepath}")
    print('\n\n\n')

