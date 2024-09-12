import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import axios from 'axios';

const API_URL = '/api';

function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/login`, {}, {
        auth: { username, password }
      });
      setToken(response.data.token);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" required />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  );
}

function AddSalesData({ token }) {
  const [formData, setFormData] = useState({
    date: '',
    product_name: '',
    quantity: '',
    price: '',
    additional_info: {}
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/add_sales_data`, formData, {
        headers: { Authorization: token }
      });
      alert('Sales data added successfully!');
    } catch (error) {
      console.error('Failed to add sales data:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="date" name="date" value={formData.date} onChange={handleChange} required />
      <input type="text" name="product_name" value={formData.product_name} onChange={handleChange} placeholder="Product Name" required />
      <input type="number" name="quantity" value={formData.quantity} onChange={handleChange} placeholder="Quantity" required />
      <input type="number" name="price" value={formData.price} onChange={handleChange} placeholder="Price" required />
      <button type="submit">Add Sales Data</button>
    </form>
  );
}

function AskQuestion({ token }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/ask`, { question }, {
        headers: { Authorization: token }
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Failed to get answer:', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask a question" required />
        <button type="submit">Ask</button>
      </form>
      {answer && <p>{answer}</p>}
    </div>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  React.useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  if (!token) {
    return <Login setToken={setToken} />;
  }

  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/add">Add Sales Data</Link></li>
            <li><Link to="/ask">Ask Question</Link></li>
          </ul>
        </nav>

        <Routes>
          <Route path="/add" element={<AddSalesData token={token} />} />
          <Route path="/ask" element={<AskQuestion token={token} />} />
          <Route path="/" element={<h1>Welcome to Sales Data Dashboard</h1>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;