import React, { useEffect, useRef } from 'react';

function HeroSection() {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.src = 'http://127.0.0.1:5000/video_feed';
    }
  }, []);

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

export default HeroSection;