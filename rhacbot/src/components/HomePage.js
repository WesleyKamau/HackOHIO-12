// src/components/HomePage.jsx
import React from 'react';
import { Button, Typography } from 'antd';
import { useNavigate } from 'react-router-dom'; // For v6
import './HomePage.css';
import { ENV } from '../api';

const { Title, Paragraph } = Typography;

function HomePage() {
  const navigate = useNavigate();

  const handleAddChatClick = () => {
    navigate('/add-chat');
  };

  const handleSendMessageClick = () => {
    navigate('/send-message');
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh', // Full viewport height
      }}
    >
      <div
        style={{
          maxWidth: '60vw',
          width: '100%',
          margin: '0 auto', // Center horizontally
          padding: '20px',
          backgroundColor: 'rgba(255, 255, 255, 1)', // Opaque white background
          borderRadius: '15px', // Curved edges
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', // Optional shadow for depth
        }}>
        {/* Environment badge (small, top-right) */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <div
            style={{
              fontSize: '12px',
              padding: '4px 8px',
              borderRadius: '12px',
              backgroundColor: ENV === 'development' ? '#f0ad4e' : '#5cb85c',
              color: '#fff',
              fontWeight: 600,
            }}
            title={`Environment: ${ENV}`}>
            {ENV}
          </div>
        </div>
            <div className="homepage-container">
            <img src={process.env.PUBLIC_URL + '/rhac-logo.png'} alt="RHAC Logo" className="logo" />
            <Title level={2} style={{ textAlign: 'center' }}>
                Welcome to the RHACbot Control Panel!
            </Title>
            <Paragraph style={{ textAlign: 'center' }}>
                This platform allows RHAC members to manage floor chats and send messages to specific buildings or regions. You can add new floor chats or send announcements to residents.
            </Paragraph>
            <div className="button-group">
                <Button type="primary" size="large" onClick={handleAddChatClick}>
                Add Floor Chat
                </Button>
                <Button type="primary" size="large" onClick={handleSendMessageClick}>
                Send Message
                </Button>
            </div>
        </div>
        </div>
    </div>
  );
}

export default HomePage;
