import csv
import os
import pandas as pd
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from urllib.parse import urlparse, parse_qs
from pymongo import MongoClient
import json
import os
from parse_youtube import get_video_id, get_youtube_data, get_youtube_transcript

# MongoDB connection string from test_mongo.py
uri = "mongodb+srv://rohit98kumar:War14Par%40@cluster0.u3tzcib.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        return client
    except Exception as e:
        print("❌ Connection failed:", e)
        return None

def insert_videos_to_collection(client, url):
    """Insert video data into MongoDB collection"""
    try:
        # Select database and collection
        db = client['real_estate_tours']  # Changed from 'real_estate_snippet' to 'real_estate_tours'
        collection = db['snippets']  # Collection name
        
        # Get video data from URL
        video_data = get_youtube_data(url)
        
        # Get transcript data
        transcript = get_youtube_transcript(url)
        
        # Prepare single document for insertion
        document = {
            "video_id": video_data['video_id'],
            "title": video_data['title'],
            "thumbnail": video_data['thumbnail'],
            "description": video_data['description'],
            "url": video_data['url'],
            "transcript": transcript,
            "created_at": datetime.now().isoformat()
        }
        
        # Insert single document
        result = collection.insert_one(document)
        print(f"✅ Successfully inserted video: {video_data['title']}")
        print(f"Inserted ID: {result.inserted_id}")
        
        return True
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return False

def retrieve_videos_from_collection(client):
    """Retrieve all video data from MongoDB collection"""
    try:
        # Select database and collection (same as insert function)
        db = client['real_estate_tours']
        collection = db['snippets']
        
        # Retrieve all documents and convert to list of dictionaries with 'id' field
        videos = [
            {
                "id": doc.get('video_id', ''),  # Changed from video_id to id
                "title": doc.get('title', ''),
                "thumbnail": doc.get('thumbnail', ''),
                "description": doc.get('description', ''),
                "url": doc.get('url', ''),
                "created_at": doc.get('created_at', '')
            }
            for doc in collection.find({}, {'_id': 0})
        ]
        
        print(f"✅ Successfully retrieved {len(videos)} videos from MongoDB")
        return videos
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return []

def delete_video_from_collection(client, video_id):
    """Delete a specific video from MongoDB collection by video_id"""
    try:
        # Select database and collection (same as other functions)
        db = client['real_estate_tours']
        collection = db['snippets']
        
        # Delete the document with the specified video_id
        result = collection.delete_one({'video_id': video_id})
        
        if result.deleted_count > 0:
            print(f"✅ Successfully deleted video with ID: {video_id}")
            return True
        else:
            print(f"⚠️ No video found with ID: {video_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting video: {e}")
        return False

if __name__ == "__main__":
    # Test the get_youtube_transcript function
    print("🔄 Testing transcript fetching...")
    test_url = "https://www.youtube.com/watch?v=uRbG2pnWumM&t=3s"
    transcript = get_youtube_transcript(test_url)
    
    if transcript:
        print(f"\n✅ Transcript fetched successfully ({len(transcript)} characters)")
    else:
        print("\n⚠️ No transcript found or error occurred")
    
    # Test MongoDB connection and insertion with transcript
    print("\n🔄 Testing MongoDB connection and insertion...")
    client = connect_to_mongodb()
    
    if client:
        # Test insertion with transcript
        insert_result = insert_videos_to_collection(client, test_url)
        
        if insert_result:
            print("\n✅ Video with transcript inserted successfully")
        else:
            print("\n⚠️ Failed to insert video")
        
        client.close()
        print("\n🔒 MongoDB connection closed")
    else:
        print("❌ Could not connect to MongoDB")