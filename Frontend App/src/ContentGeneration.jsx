import React, { useState } from 'react';

function ContentGeneration() {
  const [url, setUrl] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null); // Add session_id state
  const [applyLoading, setApplyLoading] = useState(false); // Add loading state for apply button

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
          setSessionId(data.session_id); // Store session_id
          setShowForm(true);
        } else {
          console.error('Failed to fetch title and description');
          // Fallback to hardcoded values if API fails
          setTitle('This is my sample title');
          setDescription('This is my description. This is my description...');
          setSessionId(null);
          setShowForm(true);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        // Fallback to hardcoded values if API fails
        setTitle('Failed to get title.');
        setDescription('Failed to get description.');
        setSessionId(null);
        setShowForm(true);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleApply = async () => {
    if (!sessionId) {
      console.error('No session ID available');
      alert('Please generate title and description first');
      return;
    }

    if (!feedback.trim()) {
      alert('Please provide feedback before applying');
      return;
    }

    setApplyLoading(true);
    try {
      const response = await fetch('http://localhost:8000/feedback_title_description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_feedback: feedback
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Update title and description with the feedback-improved versions
        setTitle(data.title);
        setDescription(data.description);
        setFeedback(''); // Clear feedback input
        console.log('Feedback applied successfully:', data);
      } else {
        const errorData = await response.json();
        console.error('Failed to apply feedback:', errorData);
        alert('Failed to apply feedback. Please try again.');
      }
    } catch (error) {
      console.error('Error applying feedback:', error);
      alert('Error applying feedback. Please try again.');
    } finally {
      setApplyLoading(false);
    }
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
              rows={16}
            />
          </div>
          
          <div className="form-group">
            <label>Feedback</label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="form-textarea feedback-textarea"
              rows={8}
              placeholder="Enter your feedback to improve title and description"
            />
            <button 
              onClick={handleApply} 
              className="apply-btn"
              disabled={applyLoading || !sessionId}
            >
              {applyLoading ? 'APPLYING...' : 'Apply'}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

export default ContentGeneration;