import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function NavBar({ token, setToken }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    setToken(null);
    navigate('/login');
  };

  return (
    <nav>
      {token ? (
        <>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/add">Add Sales Data</Link></li>
          <li><Link to="/ask">Ask Question</Link></li>
          <li><button onClick={handleLogout}>Logout</button></li>
        </>
      ) : (
        <>
          <li><Link to="/login">Login</Link></li>
          <li><Link to="/register">Register</Link></li>
        </>
      )}
    </nav>
  );
}

export default NavBar;