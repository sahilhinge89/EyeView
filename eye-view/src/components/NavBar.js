// src/components/NavBar.js (updated)

import React from 'react';
import { Link } from 'react-router-dom';

function NavBar() {
  return (
    <nav className="navbar">
      <div className="logo">EyeView</div>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/video_feed">Alert</Link></li>
        <li><Link to="#features">History</Link></li>
        <li><Link to="#pricing">About</Link></li>
        <li><a href="mailto:contact@eyeview.com" className="contact-link">Contact Us</a></li>
      </ul>
      <div className="nav-actions">
        <Link to="/login"><button className="login-btn">Login</button></Link>
        <Link to="/signup"><button className="signup-btn">Sign Up</button></Link>
      </div>
    </nav>
  );
}

export default NavBar;