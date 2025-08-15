import React, { useState, useEffect } from 'react';
import videoData from './videoData';

function VideoStore() {
  const [urlInput, setUrlInput] = useState('');
  const [videos, setVideos] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const videosPerPage = 8;

  // Fetch videos from FastAPI
  useEffect(() => {
    fetch('http://localhost:8000/videos')
      .then(response => response.json())
      .then(data => setVideos(data))
      .catch(error => console.error('Error:', error));
  }, []);

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (urlInput.trim()) {
      try {
        const response = await fetch('http://localhost:8000/videos', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: urlInput.trim() })
        });
        
        if (response.ok) {
          const newVideo = await response.json();
          setVideos(prevVideos => [...prevVideos, newVideo]);
          setUrlInput('');
          console.log('Video added successfully:', newVideo);
        } else {
          const error = await response.json();
          console.error('Error adding video:', error.detail);
          alert(`Error: ${error.detail}`);
        }
      } catch (error) {
        console.error('Network error:', error);
        alert('Failed to add video. Please check your connection.');
      }
    }
  };

  // Remove video function (placeholder for now)
  const remove_video = async (video_id) => {
    try {
      // Encode the video ID for the URL
      const encodedVideoId = encodeURIComponent(video_id);
      
      const response = await fetch(`http://localhost:8000/videos/${encodedVideoId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        // Remove video from local state
        setVideos(prevVideos => prevVideos.filter(video => video.id !== video_id));
        console.log('Video removed successfully:', video_id);
      } else {
        const error = await response.json();
        console.error('Error removing video:', error.detail);
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Network error:', error);
      alert('Failed to remove video. Please check your connection.');
    }
  };

  // Pagination logic
  const indexOfLastVideo = currentPage * videosPerPage;
  const indexOfFirstVideo = indexOfLastVideo - videosPerPage;
  const currentVideos = videos.slice(indexOfFirstVideo, indexOfLastVideo);
  const totalPages = Math.ceil(videos.length / videosPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <main className="main">
      <h1>Video Store</h1>
      
      <div className="url-input-section">
        <form onSubmit={handleUrlSubmit} className="url-form">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Enter video URL..."
            className="url-input"
          />
          <button type="submit" className="submit-btn">Add Video</button>
        </form>
      </div>

      <div className="video-grid">
        {currentVideos.map((video) => (
          <div key={video.id} className="video-item">
            <button 
              className="remove-btn"
              onClick={() => remove_video(video.id)}
              title="Remove video"
            >
              ×
            </button>
            <div className="video-snippet">
              <img 
                src={video.thumbnail} 
                alt={video.title}
                className="video-thumbnail"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgZmlsbD0iI2Y1ZjJlZCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNjY2Ij5WaWRlbyBTbmlwcGV0PC90ZXh0Pjwvc3ZnPg==';
                }}
              />
              <div className="video-overlay">Video Snippet</div>
            </div>
            <div className="video-content">
              <h3 className="video-title">{video.title}</h3>
              <p className="video-description">{video.description}</p>
              <a href={video.url} target="_blank" rel="noopener noreferrer" className="video-link">
                Watch Video
              </a>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i + 1}
              onClick={() => paginate(i + 1)}
              className={`page-btn ${currentPage === i + 1 ? 'active' : ''}`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}
    </main>
  );
}

export default VideoStore;