import React, { useState, useEffect } from 'react';

function Search() {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [hasSearched, setHasSearched] = useState(false);
  const [videoData, setVideoData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const videosPerPage = 4;
  const maxResults = 10;

  // Function to fetch data from backend
  const fetchVideoData = async (searchText) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/search_results?text=${encodeURIComponent(searchText)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch video data');
      }
      const data = await response.json();
      setVideoData(data);
    } catch (err) {
      setError(err.message);
      setVideoData([]);
    } finally {
      setLoading(false);
    }
  };

  // Always show all videos from API when search is performed
  const filteredVideos = hasSearched 
    ? videoData.slice(0, maxResults)
    : [];

  const totalPages = Math.ceil(filteredVideos.length / videosPerPage);
  const startIndex = (currentPage - 1) * videosPerPage;
  const currentVideos = filteredVideos.slice(startIndex, startIndex + videosPerPage);

  const handleSearch = () => {
    setHasSearched(true);
    setCurrentPage(1);
    fetchVideoData(searchTerm);
  };

  const goToPage = (page) => {
    setCurrentPage(page);
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Helper function to format time
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <main className="main">
      <h1>Search Videos</h1>
      
      <div className="search-section">
        <input
          type="text"
          placeholder="Search videos..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <button onClick={handleSearch} className="search-btn" disabled={loading}>
          {loading ? 'Loading...' : 'Search'}
        </button>
      </div>

      {!hasSearched && (
        <div className="no-search-message">
          <p>Click "Search" to view all videos</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {hasSearched && !loading && !error && filteredVideos.length > 0 && (
        <div className="video-grid">
          {currentVideos.map((video) => (
            <div key={video.id} className="video-item">
              <div className="video-snippet">
                <img 
                  src={video.thumbnail} 
                  alt={video.title}
                  className="video-thumbnail"
                  onError={(e) => {
                    e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgZmlsbD0iI2Y1ZjJlZCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNjY2Ij5WaWRlbyBTbmlwcGV0PC90ZXh0Pjwvc3ZnPg==';
                  }}
                />
                <div className="video-overlay">
                  <span className="video-duration">
                    {formatTime(video.start)} - {formatTime(video.end)}
                  </span>
                </div>
              </div>
              <div className="video-content">
                <h3 className="video-title">
                  <a href={video.url} target="_blank" rel="noopener noreferrer">
                    {video.title}
                  </a>
                </h3>
                <div className="video-description-container">
                  <p className="video-description">{video.content}</p>
                  <span className="video-score">Relevance Score: {video.score?.toFixed(3) || 'N/A'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {hasSearched && !loading && !error && filteredVideos.length > 0 && totalPages > 1 && (
        <div className="pagination">
          {[...Array(Math.min(3, totalPages))].map((_, index) => (
            <button
              key={index + 1}
              onClick={() => goToPage(index + 1)}
              className={`page-btn ${currentPage === index + 1 ? 'active' : ''}`}
            >
              {index + 1}
            </button>
          ))}
          {totalPages > 3 && (
            <>
              <span className="pagination-dots">......</span>
              <button onClick={goToNextPage} className="page-btn next-btn">
                Next
              </button>
            </>
          )}
        </div>
      )}
    </main>
  );
}

export default Search;