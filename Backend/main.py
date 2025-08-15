from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import csv
import os
import pandas as pd
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from youtube_to_mongo import get_youtube_data, connect_to_mongodb, insert_videos_to_collection, retrieve_videos_from_collection, delete_video_from_collection
from youtube_to_pinecone import connect_to_pinecone, insert_videos_to_collection as insert_videos_to_pinecone, delete_video_from_collection as delete_from_pinecone

class Video(BaseModel):
    id: str  # Change from int to str
    title: str
    url: str
    thumbnail: str
    description: str

# Simplified VideoCreate model - only needs URL
class VideoCreate(BaseModel):
    url: str

app = FastAPI(debug=True)

# Function to generate localhost origins for a port range
def generate_localhost_origins(start_port: int, end_port: int) -> List[str]:
    return [f"http://localhost:{port}" for port in range(start_port, end_port + 1)]

# Generate origins from port 5173 to 6200 (extended range)
origins = generate_localhost_origins(5173, 6200) + [
    "http://localhost:3000"  # Keep existing port 3000
]

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get all videos
@app.get("/videos", response_model=List[Video])
def get_videos():
    try:
        client = connect_to_mongodb()
        if client:
            videos = retrieve_videos_from_collection(client)
            client.close()
            return videos
        else:
            return []
    except Exception as e:
        print(f"❌ Error retrieving videos: {e}")
        return []

# Add a new video
@app.post("/videos")
def add_video(video: VideoCreate):
    mongo_client = None
    pinecone_index = None
    video_inserted_to_mongo = False
    video_inserted_to_pinecone = False
    video_data = None
    
    def rollback_insertions():
        """Helper function to rollback any successful insertions"""
        if video_inserted_to_mongo and mongo_client and video_data:
            try:
                delete_video_from_collection(mongo_client, video_data['video_id'])
                print(f"🔄 Rolled back MongoDB insertion for video: {video_data['video_id']}")
            except Exception as rollback_error:
                print(f"❌ Failed to rollback MongoDB insertion: {rollback_error}")
        
        if video_inserted_to_pinecone and pinecone_index and video_data:
            try:
                from youtube_to_pinecone import delete_video_from_collection as delete_from_pinecone
                delete_from_pinecone(pinecone_index, video_data['video_id'])
                print(f"🔄 Rolled back Pinecone insertion for video: {video_data['video_id']}")
            except Exception as rollback_error:
                print(f"❌ Failed to rollback Pinecone insertion: {rollback_error}")
    
    try:
        # Connect to MongoDB
        mongo_client = connect_to_mongodb()
        if not mongo_client:
            raise HTTPException(status_code=500, detail="MongoDB connection failed")
        
        # Connect to Pinecone
        pinecone_index = connect_to_pinecone()
        if not pinecone_index:
            raise HTTPException(status_code=500, detail="Pinecone connection failed")
        
        # Check if video already exists in MongoDB
        existing_videos = retrieve_videos_from_collection(mongo_client)
        video_data = get_youtube_data(video.url)
        
        existing_video = next((v for v in existing_videos if v["id"] == video_data['video_id']), None)
        if existing_video:
            raise HTTPException(status_code=400, detail="Video already exists")
        
        # Attempt to insert into MongoDB first
        mongo_success = insert_videos_to_collection(mongo_client, video.url)
        if not mongo_success:
            raise Exception("Failed to insert video into MongoDB")
        video_inserted_to_mongo = True
        
        # Attempt to insert into Pinecone
        pinecone_success = insert_videos_to_pinecone(pinecone_index, video.url)
        if not pinecone_success:
            raise Exception("Failed to insert video into Pinecone")
        video_inserted_to_pinecone = True
        
        # If both operations succeed, return the new video data
        new_video = {
            "id": video_data['video_id'],
            "title": video_data['title'],
            "url": video_data['url'],
            "thumbnail": video_data['thumbnail'],
            "description": video_data['description']
        }
        print(f"✅ Video successfully inserted into both MongoDB and Pinecone: {video_data['title']}")
        return new_video
        
    except HTTPException:
        rollback_insertions()
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        rollback_insertions()
        print(f"❌ Error adding video: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Clean up connections
        if mongo_client:
            mongo_client.close()

# Remove a video
@app.delete("/videos/{video_id}")
def remove_video(video_id: str):
    mongo_client = None
    pinecone_index = None
    video_deleted_from_mongo = False
    video_deleted_from_pinecone = False
    
    def rollback_deletions():
        """Helper function to rollback any successful deletions by re-inserting"""
        # Note: This would require storing the original video data before deletion
        # For now, we'll just log the rollback attempt
        if video_deleted_from_mongo:
            print(f"⚠️ MongoDB deletion succeeded but Pinecone failed for video: {video_id}")
            print(f"⚠️ Manual intervention may be required to restore consistency")
        
        if video_deleted_from_pinecone:
            print(f"⚠️ Pinecone deletion succeeded but MongoDB failed for video: {video_id}")
            print(f"⚠️ Manual intervention may be required to restore consistency")
    
    try:
        # Connect to MongoDB
        mongo_client = connect_to_mongodb()
        if not mongo_client:
            raise HTTPException(status_code=500, detail="MongoDB connection failed")
        
        # Connect to Pinecone
        pinecone_index = connect_to_pinecone()
        if not pinecone_index:
            raise HTTPException(status_code=500, detail="Pinecone connection failed")
        
        # Attempt to delete from MongoDB first
        mongo_success = delete_video_from_collection(mongo_client, video_id)
        if not mongo_success:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found in MongoDB")
        video_deleted_from_mongo = True
        
        # Attempt to delete from Pinecone
        pinecone_success = delete_from_pinecone(pinecone_index, video_id)
        if not pinecone_success:
            raise Exception(f"Failed to delete video {video_id} from Pinecone")
        video_deleted_from_pinecone = True
        
        # If both operations succeed
        print(f"✅ Video {video_id} successfully deleted from both MongoDB and Pinecone")
        return {"message": f"Video {video_id} successfully deleted from both databases"}
        
    except HTTPException:
        rollback_deletions()
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        rollback_deletions()
        print(f"❌ Error deleting video: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Clean up connections
        if mongo_client:
            mongo_client.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)