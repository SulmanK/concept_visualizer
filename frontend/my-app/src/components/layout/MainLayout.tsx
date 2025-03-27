import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';

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
  
  return (
    <div className="flex flex-col min-h-screen">
      <Header activeRoute={location.pathname} />
      
      <main className={`flex-grow py-6 px-4 sm:px-6 lg:px-8 ${className}`}>
        <div className="max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
      
      <Footer />
    </div>
  );
}; 