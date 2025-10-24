// src/App.jsx
import React, { useRef, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AddChatPage from './components/AddChatPage';
import SendMessagePage from './components/SendMessagePage';
import HomePage from './components/HomePage';

function App() {
  const vantaRef = useRef(null);
  // Feature flag: enable the Vanta background only when REACT_APP_STYLISH is set to a truthy value
  const stylishEnv = (process.env.REACT_APP_STYLISH || process.env.STYLISH || '').toString().toLowerCase();
  const stylishEnabled = ['1', 'true', 'yes', 'on'].includes(stylishEnv);
  // Determine Router basename:
  // - If REACT_APP_BASENAME is set, use it
  // - In development use an empty basename so routes are rooted at '/'
  // - In production default to '/RHACbot'
  const basename = process.env.REACT_APP_BASENAME ?? (process.env.NODE_ENV === 'development' ? '' : '/RHACbot');

  useEffect(() => {

    // Only attempt to load Vanta if the feature flag is enabled
    if (stylishEnabled) {
      const loadVanta = () => {
        if (window.VANTA) {
          window.VANTA.FOG({
            el: vantaRef.current,
            mouseControls: true,
            touchControls: true,
            gyroControls: false,
            minHeight: 200.0,
            minWidth: 200.0,
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
    }

    return () => {
      if (vantaRef.current && vantaRef.current.vantaEffect) {
        vantaRef.current.vantaEffect.destroy();
      }
    };
  });

  // If stylish is disabled, use a simple solid gray background instead of Vanta.
  // Ensure the background covers the full viewport height (min-h-screen).
  const containerClass = stylishEnabled
    ? 'vanta-container flex flex-col items-center justify-center min-h-screen w-full'
    : 'flex flex-col items-center justify-center min-h-screen w-full bg-gray-200';

  // Inline style fallback for non-stylish mode so background is gray even if Tailwind
  // classes aren't applied (useful in environments where CSS isn't loaded).
  const nonStylishStyle = { minHeight: '100vh', width: '100%', backgroundColor: '#888888ff' }; // bg-gray-200

  return (
    <div ref={vantaRef} className={containerClass} style={stylishEnabled ? undefined : nonStylishStyle}>
      <div style={{ zIndex: 100 }}>
        <Router basename={basename}>
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
