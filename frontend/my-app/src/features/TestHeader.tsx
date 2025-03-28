import React from 'react';
import { Header } from '../components/layout/Header';

export const TestHeader: React.FC = () => {
  const pageStyle = {
    minHeight: '100vh',
    background: 'linear-gradient(to bottom right, #EEF2FF, #C7D2FE)',
    fontFamily: 'Montserrat, system-ui, -apple-system, sans-serif',
    color: '#1F2937'
  };

  const mainStyle = {
    maxWidth: '80rem',
    margin: '0 auto',
    padding: '2rem 1rem'
  };

  const headingStyle = {
    fontSize: '1.875rem',
    fontWeight: 'bold',
    color: '#312E81',
    marginBottom: '0.5rem'
  };

  const subtitleStyle = {
    fontSize: '1.125rem',
    color: '#4F46E5',
    marginBottom: '2rem'
  };

  const cardStyle = {
    background: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(4px)',
    borderRadius: '0.5rem',
    boxShadow: '0 10px 30px -5px rgba(79, 70, 229, 0.2)',
    border: '1px solid #e0e7ff',
    padding: '1.5rem',
    marginBottom: '2rem'
  };

  const cardTitleStyle = {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#312E81',
    marginBottom: '1.5rem'
  };

  return (
    <div style={pageStyle}>
      <Header activeRoute="/create" />
      
      <main style={mainStyle}>
        <div>
          <h2 style={headingStyle}>Test Header Page</h2>
          <p style={subtitleStyle}>
            This page is used to test the header component in isolation.
          </p>
        </div>

        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Header Component Test</h3>
          <p>The header above should match the following specs from the mockup:</p>
          <ul style={{listStyleType: 'disc', paddingLeft: '1.25rem', marginTop: '1rem'}}>
            <li style={{marginBottom: '0.5rem'}}>White background with 80% opacity and slight blur effect</li>
            <li style={{marginBottom: '0.5rem'}}>Standard height (h-16) matching mockup</li>
            <li style={{marginBottom: '0.5rem'}}>Logo circle with gradient background (from-primary to-primary-dark)</li>
            <li style={{marginBottom: '0.5rem'}}>Title with gradient text (from-primary to-secondary)</li>
            <li style={{marginBottom: '0.5rem'}}>Navigation links with rounded-lg (not rounded-full)</li>
            <li style={{marginBottom: '0.5rem'}}>Active state with gradient background and shadow</li>
            <li style={{marginBottom: '0.5rem'}}>Proper font weights and spacing between elements</li>
            <li style={{marginBottom: '0.5rem'}}>Bottom border for separation from content</li>
          </ul>
        </div>
      </main>
    </div>
  );
}; 