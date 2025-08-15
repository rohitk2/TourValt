import { useState } from 'react';
import './App.css';
import ContentGeneration from './ContentGeneration';
import Search from './Search';
import VideoStore from './VideoStore';

function App() {
  const [currentPage, setCurrentPage] = useState('video-store');

  const renderPage = () => {
    switch (currentPage) {
      case 'content-generation':
        return <ContentGeneration />;
      case 'search':
        return <Search />;
      case 'video-store':
      default:
        return <VideoStore />;
    }
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="logo-section" onClick={() => setCurrentPage('video-store')} style={{ cursor: 'pointer' }}>
            <div className="text-logo">TV</div>
            <span className="brand-name">TourValt</span>
          </div>
          <nav className="nav-links">
            <button 
              className={`nav-link ${currentPage === 'search' ? 'active' : ''}`}
              onClick={() => setCurrentPage('search')}
            >
              Search
            </button>
            <button 
              className={`nav-link ${currentPage === 'content-generation' ? 'active' : ''}`}
              onClick={() => setCurrentPage('content-generation')}
            >
              Content Generation
            </button>
            <button 
              className={`nav-link ${currentPage === 'video-store' ? 'active' : ''}`}
              onClick={() => setCurrentPage('video-store')}
            >
              Video Store
            </button>
          </nav>
        </div>
      </header>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
