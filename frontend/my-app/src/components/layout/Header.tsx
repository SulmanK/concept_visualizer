import React from 'react';
import { Link } from 'react-router-dom';

export interface HeaderProps {
  /**
   * The current active route
   */
  activeRoute?: string;
}

/**
 * Application header with navigation
 */
export const Header: React.FC<HeaderProps> = ({ activeRoute = '/' }) => {
  const navItems = [
    { label: 'Create', path: '/', icon: '✨' },
    { label: 'Refine', path: '/refine', icon: '🔄' },
    { label: 'Gallery', path: '/gallery', icon: '🖼️' },
  ];
  
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-gradient-primary rounded-full flex items-center justify-center text-white font-bold shadow-glow">
                CV
              </div>
            </div>
            <h1 className="ml-3 text-xl font-semibold text-dark-900 flex items-center">
              <span className="bg-gradient-to-r from-primary-600 to-accent-600 text-transparent bg-clip-text">
                Concept Visualizer
              </span>
            </h1>
          </div>
          
          {/* Navigation */}
          <nav className="flex space-x-4">
            {navItems.map(item => {
              const isActive = activeRoute === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    px-3 py-2 rounded-md text-sm font-medium
                    ${isActive 
                      ? 'text-primary-700 bg-primary-50 shadow-sm'
                      : 'text-dark-600 hover:text-primary-600 hover:bg-primary-50'
                    }
                    transition-colors duration-150
                  `}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <span className="mr-1">{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}; 