// src/components/AskQuestion.js

import React, { useState } from 'react';
import axios from '../axiosConfig';

function AskQuestion() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setAnswer('');
    setLoading(true);
    try {
      const response = await axios.post('/ask', { question });
      setAnswer(response.data.answer);
    } catch (error) {
      setError('Failed to get answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Ask a Question</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask a question" required />
        <button type="submit" disabled={loading}>{loading ? 'Asking...' : 'Ask'}</button>
      </form>
      {error && <p style={{color:'red'}}>{error}</p>}
      {answer && <div><h3>Answer:</h3><p>{answer}</p></div>}
    </div>
  );
}

export default AskQuestion;
