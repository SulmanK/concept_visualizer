import React from 'react';
import { Link } from 'react-router-dom';

export interface HeaderProps {
  /**
   * The current active route
   */
  activeRoute?: string;
}

/**
 * Application header with navigation using Tailwind CSS
 */
export const Header: React.FC<HeaderProps> = ({ activeRoute = '/' }) => {
  // Consider both '/' and '/create' as the create route since they show the same component
  const isCreateRoute = activeRoute === '/' || activeRoute === '/create';
  
  return (
    <header className="w-full bg-white/80 backdrop-blur-sm shadow-sm border-b border-indigo-100 sticky top-0 left-0 right-0 z-100 m-0 p-0">
      <div className="w-full max-w-7xl mx-auto px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and title */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center no-underline">
              <div className="h-10 w-10 bg-gradient-to-r from-primary to-primary-dark shadow-modern flex items-center justify-center text-white font-bold rounded-full">
                CV
              </div>
              <h1 className="ml-3 text-xl font-bold gradient-text">
                Concept Visualizer
              </h1>
            </Link>
          </div>
          
          {/* Navigation */}
          <nav className="flex gap-4">
            <Link 
              to="/create" 
              className={isCreateRoute ? "nav-link nav-link-active" : "nav-link nav-link-inactive"}
            >
              <span className="mr-2">✨</span>Create
            </Link>
            
            <Link 
              to="/recent" 
              className={activeRoute === '/recent' ? "nav-link nav-link-active" : "nav-link nav-link-inactive"}
            >
              <span className="mr-2">📚</span>Recent
            </Link>
            
            <Link 
              to="/refine" 
              className={activeRoute.includes('/refine') ? "nav-link nav-link-active" : "nav-link nav-link-inactive"}
            >
              <span className="mr-2">🔄</span>Refine
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

// Add default export to fix import issue
export default Header; 