import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';
import './App.css'; // Ensure custom styles are linked

// Connect to Flask backend at localhost:5000
const socket = io(' http://127.0.0.1:5000');

function App() {
  return (
    <div className="app">
      <Sidebar />
      <MainContent />
    </div>
  );
}

// Sidebar Component (Left side menu)
function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>EyeView</h2>
      </div>
      <nav>
        <a href="#">Dashboard</a>
        <a href="#">Admin</a>
        <a href="#">Alert</a>
        <a href="#">Live Cam</a>
        <a href="#">History</a>
        <a href="#">Control Panel</a>
      </nav>
      <div className="logout">
        <a href="#">Logout</a>
      </div>
    </div>
  );
}

// Top bar (search and notification with dropdown)
function TopBar() {
  return (
    <div className="topbar">
      <div className="search-bar">
        <input type="text" placeholder="Search..." />
      </div>
      <div className="top-actions">
        <span className="icon"></span>
        <span className="icon"></span>
        <UserDropdown />
      </div>
    </div>
  );
}

// Dropdown menu for profile, settings, logout
function UserDropdown() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="dropdown">
      <a
        href="#"
        className="d-block link-body-emphasis text-decoration-none dropdown-toggle"
        onClick={toggleDropdown}
        style={{ display: 'flex', alignItems: 'center' }}
      >
        <img
          src="https://github.com/mdo.png"
          alt="mdo"
          width="32"
          height="32"
          className="circular-img"
        />
      </a>

      {isOpen && (
        <ul
          className="dropdown-menu text-small show"
          style={{ position: 'absolute', right: 0, marginTop: '10px', listStyleType: 'none' }}
        >
          <li>
            <a className="dropdown-item" href="#">
              Profile
            </a>
          </li>
          <li>
            <a className="dropdown-item" href="#">
              Settings
            </a>
          </li>
          <li>
            <hr className="dropdown-divider" />
          </li>
          <li>
            <a className="dropdown-item" href="#">
              Logout
            </a>
          </li>
        </ul>
      )}
    </div>
  );
}

// Main content (selected live camera and other cams)
function MainContent() {
  const videoRef = useRef(null);
  const [alerts, setAlerts] = useState([]); // State to hold alerts

  useEffect(() => {
    // Listen for alerts from the server
    socket.on('alert', (data) => {
      console.log('Received alert:', data);
      setAlerts(prevAlerts => [...prevAlerts, data]); // Add new alert to state
    });

    // Clean up socket connection on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    const videoElement = videoRef.current;

    // Clean up the video source when the component unmounts
    return () => {
      if (videoElement) {
        videoElement.src = '';
      }
    };
  }, []);

  return (
    <div className="main-content">
      <TopBar />

      <div className="camera-feed">
        <img
          src=" http://127.0.0.1:5000/video_feed"
          alt="Live Camera Feed"
          className="video-feed"
        />
      </div>

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
