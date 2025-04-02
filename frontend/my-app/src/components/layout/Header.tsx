import React, { useState } from 'react';
import { Link } from 'react-router-dom';

export interface HeaderProps {
  /**
   * The current active route
   */
  activeRoute?: string;
}

/**
 * Application header with navigation using Tailwind CSS
 * Includes responsive mobile menu for smaller screens
 */
export const Header: React.FC<HeaderProps> = ({ activeRoute = '/' }) => {
  // Consider both '/' and '/create' as the create route since they show the same component
  const isCreateRoute = activeRoute === '/' || activeRoute === '/create';
  
  // State for mobile menu toggle
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };
  
  return (
    <header className="w-full bg-white/80 backdrop-blur-sm shadow-sm border-b border-indigo-100 sticky top-0 left-0 right-0 z-100 m-0 p-0">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-14 sm:h-16">
          {/* Logo and title */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center no-underline">
              <div className="h-8 w-8 sm:h-10 sm:w-10 bg-gradient-to-r from-primary to-primary-dark shadow-modern flex items-center justify-center text-white font-bold rounded-full">
                CV
              </div>
              <h1 className="ml-2 sm:ml-3 text-lg sm:text-xl font-bold gradient-text">
                <span className="hidden sm:inline">Concept Visualizer</span>
                <span className="sm:hidden">CV</span>
              </h1>
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex gap-4">
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
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button 
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-indigo-700 hover:text-indigo-900 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
              aria-expanded="false"
              onClick={toggleMobileMenu}
            >
              <span className="sr-only">Open main menu</span>
              {/* Hamburger icon */}
              {!mobileMenuOpen ? (
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              ) : (
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile menu, show/hide based on state */}
      {mobileMenuOpen && (
        <div className="md:hidden">
          <div className="pt-2 pb-3 space-y-1 bg-white/95 px-4 shadow-lg">
            <Link 
              to="/create" 
              className={`${isCreateRoute ? "bg-indigo-100 text-indigo-800" : "text-indigo-600"} block px-3 py-3 rounded-md text-base font-medium flex items-center`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="mr-3 text-lg">✨</span>Create
            </Link>
            
            <Link 
              to="/recent" 
              className={`${activeRoute === '/recent' ? "bg-indigo-100 text-indigo-800" : "text-indigo-600"} block px-3 py-3 rounded-md text-base font-medium flex items-center`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="mr-3 text-lg">📚</span>Recent
            </Link>
            
            <Link 
              to="/refine" 
              className={`${activeRoute.includes('/refine') ? "bg-indigo-100 text-indigo-800" : "text-indigo-600"} block px-3 py-3 rounded-md text-base font-medium flex items-center`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="mr-3 text-lg">🔄</span>Refine
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};

// Add default export to fix import issue
export default Header; 