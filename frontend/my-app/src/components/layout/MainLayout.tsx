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
 * Optimized for responsive viewing across device sizes
 */
export const MainLayout: React.FC<MainLayoutProps> = ({ className = '' }) => {
  const location = useLocation();
  
  // Using Tailwind classes instead of inline styles for better responsive control
  return (
    <div className="flex flex-col min-h-screen w-full m-0 p-0 bg-gradient-to-br from-indigo-50 to-indigo-200">
      <Header activeRoute={location.pathname} />
      
      <main className={`flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 md:py-8 ${className}`}>
        <Outlet />
      </main>
      
      <Footer />
    </div>
  );
};

export default MainLayout; 