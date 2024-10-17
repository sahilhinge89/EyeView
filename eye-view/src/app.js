import React, { useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';
import './App.css'; // Custom CSS styles

// Initialize socket connection (replace with your backend URL if not localhost)
const socket = io('http://127.0.0.1:5000');

// App component
function App() {
  return (
    <div className="app">
      <NavBar />
      <HeroSection />
      <MainContent />
    </div>
  );
}

// NavBar Component
function NavBar() {
  return (
    <nav className="navbar">
      <div className="logo">EyeView</div>
      <ul className="nav-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#assets">Alert</a></li>
        <li><a href="#features">History</a></li>
        <li><a href="#pricing">About</a></li>
        <li><a href="https://mail.google.com/" className="contact-link">Contact Us</a></li>
      </ul>
      <div className="nav-actions">
        <button className="create-account">Create Account</button>
      </div>
    </nav>
  );
}

// HeroSection Component with Live Video Feed
function HeroSection() {
  return (
    <div className="hero-section">
      <div className="hero-content">
        <div className="video-container">
          <img
            src="http://127.0.0.1:5000/video_feed"
            autoPlay
            muted
            controls
            alt='Live Video Feed'
            className="live-video"
            style={{ width: "100%", height: "auto" }} // Optional: Adjust video dimensions
          />
        </div>
      </div>
    </div>
  );
}

// MainContent Component for Alerts
function MainContent() {
  const [alerts, setAlerts] = useState([]); // State to hold alerts

  useEffect(() => {
    // Listen for alerts from the server
    socket.on('alert', (data) => {
      console.log('Received alert:', data);
      setAlerts((prevAlerts) => [...prevAlerts, data]); // Add new alert to state
    });

    // Clean up socket connection on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="main-content">
      {/* Render only alerts here */}
      <div className="alerts-container">
        {alerts.map((alert, index) => (
          <div key={index} className="alert">
            {alert.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;