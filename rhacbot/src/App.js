// src/App.jsx
import {React, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AddChatPage from './components/AddChatPage';
import SendMessagePage from './components/SendMessagePage';
import HomePage from './components/HomePage';

function App() {
  const vantaRef = useRef(null);

  useEffect(() => {

    const loadVanta = () => {
      if (window.VANTA) {
        window.VANTA.FOG({
          el: vantaRef.current,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          highlightColor: '#ff0077',
          midtoneColor: '#841e10',
          lowlightColor: '#ff00d1',
        });
      }
    };

    if (window.VANTA) {
      loadVanta();
    } else {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.fog.min.js';
      script.onload = loadVanta;
      document.body.appendChild(script);
    }

    return () => {
      if (vantaRef.current && vantaRef.current.vantaEffect) {
        vantaRef.current.vantaEffect.destroy();
      }
    };
  });

  return (
    <div ref={vantaRef} className="vanta-container flex flex-col items-center justify-center h-full w-full">
      <div
      style={{
        zIndex: 100
      }}
    >
        <Router basename="RHACbot">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/add-chat" element={<AddChatPage />} />
            <Route path="/send-message" element={<SendMessagePage />} />
          </Routes>
        </Router>
      </div>
    </div>
  );
}

export default App;
