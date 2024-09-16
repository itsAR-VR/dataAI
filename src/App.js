// src/App.js

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import NavBar from './components/NavBar';
import Login from './components/Login';
import Register from './components/Register';
import AddSalesData from './components/AddSalesData';
import AskQuestion from './components/AskQuestion';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  React.useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  return (
    <Router>
      <NavBar token={token} setToken={setToken} />
      <div>
        <Routes>
          <Route path="/login" element={<Login setToken={setToken} />} />
          <Route path="/register" element={<Register />} />
          {token ? (
            <>
              <Route path="/add" element={<AddSalesData />} />
              <Route path="/ask" element={<AskQuestion />} />
              <Route path="/" element={<h1>Welcome to Sales Data Dashboard</h1>} />
            </>
          ) : (
            <>
              <Route path="/" element={<Login setToken={setToken} />} />
              <Route path="*" element={<Login setToken={setToken} />} />
            </>
          )}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
