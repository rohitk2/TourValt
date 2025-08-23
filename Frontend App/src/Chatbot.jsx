import React, { useState } from 'react';
import './Chatbot.css';

const Chatbot = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I help you today?", sender: 'bot' }
  ]);
  const [inputText, setInputText] = useState('');

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const handleSendMessage = () => {
    if (inputText.trim()) {
      const newMessage = {
        id: messages.length + 1,
        text: inputText,
        sender: 'user'
      };
      setMessages([...messages, newMessage]);
      setInputText('');
      
      // Simulate bot response
      setTimeout(() => {
        const botResponse = {
          id: messages.length + 2,
          text: "Thanks for your message! I'm here to help.",
          sender: 'bot'
        };
        setMessages(prev => [...prev, botResponse]);
      }, 1000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className={`chatbot-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {isExpanded && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <h3>Chat Assistant</h3>
            <button className="close-btn" onClick={toggleExpanded}>×</button>
          </div>
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  {message.text}
                </div>
              </div>
            ))}
          </div>
          <div className="chatbot-input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
            />
            <button onClick={handleSendMessage}>Send</button>
          </div>
        </div>
      )}
      <div className="chatbot-toggle" onClick={toggleExpanded}>
        {isExpanded ? '−' : '💬'}
      </div>
    </div>
  );
};

export default Chatbot;