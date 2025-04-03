import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import { RateLimitsPanel } from '../RateLimitsPanel';

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
  const [showRateLimits, setShowRateLimits] = useState(false);
  
  const toggleRateLimits = () => {
    setShowRateLimits(!showRateLimits);
  };
  
  // Using Tailwind classes instead of inline styles for better responsive control
  return (
    <div className="flex flex-col min-h-screen w-full m-0 p-0 bg-gradient-to-br from-indigo-50 to-indigo-200">
      <Header activeRoute={location.pathname} />
      
      <main className={`flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 md:py-8 ${className}`}>
        <Outlet />
      </main>
      
      <Footer />
      
      {/* API Rate Limits panel - fixed position */}
      <div className="fixed bottom-4 right-4 z-50">
        {showRateLimits ? (
          <RateLimitsPanel className="w-80" />
        ) : (
          <button
            onClick={toggleRateLimits}
            className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full p-3 shadow-lg flex items-center justify-center"
            title="Show API usage limits"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default MainLayout; 