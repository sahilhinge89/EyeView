import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';
import './App.css'; // Import the CSS

// Connect to Flask backend at localhost:5000
const socket = io('http://localhost:5000');

function App() {
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
        <div className="App">
            <header>
                <h1>EyeView</h1>
            </header>
            <div className="video-container">
                <img src="http://localhost:5000/video_feed" alt="Video Feed" className="video-feed" />
            </div>
            <div className="alerts-container">
                <h2>Real-Time Alerts</h2>
                {alerts.map((alert, index) => (
                    <div key={index} className="alert">{alert.message}</div>
                ))}
            </div>
        </div>
    );
}

export default App;
