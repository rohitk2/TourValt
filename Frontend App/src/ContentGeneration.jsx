import React, { useState } from 'react';

function ContentGeneration() {
  const [url, setUrl] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [feedback, setFeedback] = useState('');

  const handleGenerate = () => {
    if (url.trim()) {
      setShowForm(true);
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
        <button onClick={handleGenerate} className="generate-btn">
          GENERATE
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