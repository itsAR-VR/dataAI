// src/components/Login.js

import React, { useState } from 'react';
import axios from '../axiosConfig';
import { useNavigate } from 'react-router-dom';

function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('/login', { username, password });
      setToken(response.data.token);
      navigate('/');
    } catch (error) {
      setError('Login failed. Please check your credentials.');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      {error && <p style={{color:'red'}}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input type="text" value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username" required />
        <input type="password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      <p>Don't have an account? <a href="/register">Register here</a>.</p>
    </div>
  );
}

export default Login;
