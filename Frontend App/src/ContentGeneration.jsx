import React, { useState } from 'react';

function ContentGeneration() {
  const [url, setUrl] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (url.trim()) {
      setLoading(true);
      try {
        // Pass the URL as a query parameter
        const response = await fetch(`http://localhost:8000/title_description?url=${encodeURIComponent(url)}`);
        if (response.ok) {
          const data = await response.json();
          setTitle(data.title);
          setDescription(data.description);
          setShowForm(true);
        } else {
          console.error('Failed to fetch title and description');
          // Fallback to hardcoded values if API fails
          setTitle('This is my sample title');
          setDescription('This is my description. This is my description...');
          setShowForm(true);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        // Fallback to hardcoded values if API fails
        setTitle('Failed to get title.');
        setDescription('Failed to get description.');
        setShowForm(true);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleApply = () => {
    console.log('Applied:', { title, description, feedback });
  };

  return (
    <main className="main">
      <h1>Content Generation</h1>
      
      <div className="url-section">
        <input
          type="text"
          placeholder="URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="url-input"
        />
        <button onClick={handleGenerate} className="generate-btn" disabled={loading}>
          {loading ? 'GENERATING...' : 'GENERATE'}
        </button>
      </div>

      {showForm && (
        <div className="form-section">
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="form-input"
            />
          </div>
          
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="form-textarea"
              rows={4}
            />
          </div>
          
          <div className="form-group">
            <label>Feedback</label>
            <input
              type="text"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="form-input"
            />
            <button onClick={handleApply} className="apply-btn">
              Apply
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

export default ContentGeneration;