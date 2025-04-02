import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';

export interface MainLayoutProps {
  /**
   * Additional class names for the main content container
   */
  className?: string;
}

/**
 * Main layout component with header, footer, and content area
 */
export const MainLayout: React.FC<MainLayoutProps> = ({ className = '' }) => {
  const location = useLocation();
  
  const layoutStyle = {
    display: 'flex',
    flexDirection: 'column' as const,
    minHeight: '100vh',
    width: '100%',
    margin: 0,
    padding: 0,
    background: 'linear-gradient(to bottom right, #EEF2FF, #C7D2FE)'
  };
  
  const mainStyle = {
    flex: '1 1 auto',
    width: '100%',
    maxWidth: '1280px', 
    margin: '0 auto',
    padding: '2rem'
  };
  
  return (
    <div style={layoutStyle}>
      <Header activeRoute={location.pathname} />
      
      <main style={mainStyle}>
        <Outlet />
      </main>
      
      <Footer />
    </div>
  );
};

export default MainLayout; 