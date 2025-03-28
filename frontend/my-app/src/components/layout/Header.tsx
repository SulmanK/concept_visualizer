import React from 'react';
import { Link } from 'react-router-dom';

export interface HeaderProps {
  /**
   * The current active route
   */
  activeRoute?: string;
}

/**
 * Application header with navigation - directly implemented from the mockup HTML
 */
export const Header: React.FC<HeaderProps> = ({ activeRoute = '/' }) => {
  // Define styles as constants to avoid inline style clutter
  const headerStyle = {
    width: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(4px)',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
    borderBottom: '1px solid #e0e7ff',
    position: 'sticky' as const,
    top: 0,
    left: 0,
    right: 0,
    zIndex: 100,
    margin: 0,
    padding: 0
  };

  const containerStyle = {
    width: '100%',
    maxWidth: '1280px',
    margin: '0 auto',
    padding: '0 2rem'
  };

  const logoStyle = {
    height: '2.5rem',
    width: '2.5rem',
    background: 'linear-gradient(to right, #4F46E5, #4338CA)',
    boxShadow: '0 10px 30px -5px rgba(79, 70, 229, 0.2)'
  };

  const titleStyle = {
    marginLeft: '0.75rem',
    fontSize: '1.25rem',
    fontWeight: 700,
    background: 'linear-gradient(to right, #4F46E5, #818CF8)',
    WebkitBackgroundClip: 'text',
    backgroundClip: 'text',
    color: 'transparent'
  };

  const activeNavStyle = {
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    fontSize: '0.875rem',
    fontWeight: 600,
    background: 'linear-gradient(to right, #4F46E5, #4338CA)',
    color: 'white',
    boxShadow: '0 10px 30px -5px rgba(79, 70, 229, 0.2)'
  };

  const inactiveNavStyle = {
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#4338CA',
    transition: 'all 0.2s'
  };

  const navIconStyle = {
    marginRight: '0.5rem'
  };
  
  return (
    <header style={headerStyle}>
      <div style={containerStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '4rem' }}>
          {/* Logo and title */}
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Link to="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
              <div>
                <div style={{ ...logoStyle, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', borderRadius: '9999px' }}>
                  CV
                </div>
              </div>
              <h1 style={titleStyle}>
                Concept Visualizer
              </h1>
            </Link>
          </div>
          
          {/* Navigation */}
          <nav style={{ display: 'flex', gap: '1rem' }}>
            <Link 
              to="/create" 
              style={{...activeRoute === '/create' ? activeNavStyle : inactiveNavStyle, textDecoration: 'none'}}
            >
              <span style={navIconStyle}>✨</span>Create
            </Link>
            
            <Link 
              to="/refine" 
              style={{...activeRoute === '/refine' ? activeNavStyle : inactiveNavStyle, textDecoration: 'none'}}
            >
              <span style={navIconStyle}>🔄</span>Refine
            </Link>
            
            <Link 
              to="/gallery" 
              style={{...activeRoute === '/gallery' ? activeNavStyle : inactiveNavStyle, textDecoration: 'none'}}
            >
              <span style={navIconStyle}>🖼️</span>Gallery
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}; 