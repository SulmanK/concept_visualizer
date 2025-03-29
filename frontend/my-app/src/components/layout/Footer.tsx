import React from 'react';
import { Link } from 'react-router-dom';

export interface FooterProps {
  /**
   * Current year - defaults to current year
   */
  year?: number;
}

/**
 * Application footer with navigation and copyright - matches mockup design
 */
export const Footer: React.FC<FooterProps> = ({ 
  year = new Date().getFullYear() 
}) => {
  // Define styles as constants to avoid inline style clutter
  const footerStyle = {
    backgroundColor: '#312E81', // indigo-900
    color: '#E0E7FF', // indigo-100
    padding: '2rem 0',
    marginTop: '3rem',
    boxShadow: '0 -4px 6px -1px rgba(0, 0, 0, 0.1)',
    width: '100%'
  };

  const containerStyle = {
    width: '100%',
    maxWidth: '1280px',
    margin: '0 auto',
    padding: '0 2rem'
  };

  const gridContainerStyle = {
    display: 'flex',
    flexDirection: 'row' as const,
    flexWrap: 'wrap' as const,
    justifyContent: 'space-between',
    gap: '2rem'
  };

  const sectionStyle = {
    flex: '1',
    minWidth: '250px'
  };

  const logoContainerStyle = {
    display: 'flex',
    alignItems: 'center'
  };

  const logoStyle = {
    height: '2.5rem',
    width: '2.5rem',
    borderRadius: '9999px',
    background: 'linear-gradient(to right, #8B5CF6, #7C3AED)', // primary to primary-dark
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontWeight: 'bold',
    boxShadow: '0 10px 30px -5px rgba(139, 92, 246, 0.2)' // shadow-modern
  };

  const titleStyle = {
    marginLeft: '0.75rem',
    fontSize: '1.25rem',
    fontWeight: 700,
    color: 'white'
  };

  const descriptionStyle = {
    marginTop: '0.75rem',
    fontSize: '0.875rem',
    color: '#C7D2FE' // indigo-200
  };

  const sectionTitleStyle = {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: 'white',
    textTransform: 'uppercase' as const
  };

  const linkListStyle = {
    marginTop: '1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem'
  };

  const linkStyle = {
    fontSize: '0.875rem',
    color: '#C7D2FE', // indigo-200
    textDecoration: 'none',
    transition: 'color 0.15s ease'
  };

  const copyrightContainerStyle = {
    marginTop: '2rem',
    paddingTop: '1rem',
    borderTop: '1px solid #4F46E5', // indigo-600
    textAlign: 'center' as const
  };

  const copyrightTextStyle = {
    fontSize: '0.875rem',
    color: '#A5B4FC' // indigo-300
  };
  
  return (
    <footer style={footerStyle}>
      <div style={containerStyle}>
        <div style={gridContainerStyle}>
          {/* Left section - Logo and description */}
          <div style={sectionStyle}>
            <div style={logoContainerStyle}>
              <div style={logoStyle}>
                CV
              </div>
              <h2 style={titleStyle}>
                Concept Visualizer
              </h2>
            </div>
            <p style={descriptionStyle}>
              Create and refine visual concepts with AI
            </p>
          </div>
          
          {/* Middle section - Features */}
          <div style={sectionStyle}>
            <h3 style={sectionTitleStyle}>
              Features
            </h3>
            <ul style={linkListStyle}>
              <li>
                <Link to="/create" style={linkStyle}>
                  Create Concepts
                </Link>
              </li>
              <li>
                <Link to="/refine" style={linkStyle}>
                  Refine Concepts
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Right section - Resources */}
          <div style={sectionStyle}>
            <h3 style={sectionTitleStyle}>
              Resources
            </h3>
            <ul style={linkListStyle}>
              <li>
                <a 
                  href="https://github.com/username/concept-visualizer" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  style={linkStyle}
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a 
                  href="https://jigsawstack.com" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  style={linkStyle}
                >
                  JigsawStack API
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Copyright */}
        <div style={copyrightContainerStyle}>
          <p style={copyrightTextStyle}>
            &copy; {year} Concept Visualizer. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}; 