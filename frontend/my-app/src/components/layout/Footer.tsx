import React from 'react';
import { Link } from 'react-router-dom';

export interface FooterProps {
  /**
   * Current year - defaults to current year
   */
  year?: number;
}

/**
 * Application footer with copyright and links
 */
export const Footer: React.FC<FooterProps> = ({ 
  year = new Date().getFullYear() 
}) => {
  return (
    <footer className="bg-indigo-900 text-indigo-100 py-8 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Left section */}
          <div>
            <div className="flex items-center">
              <div className="h-10 w-10 bg-gradient-secondary rounded-full flex items-center justify-center text-white font-bold shadow-modern">
                CV
              </div>
              <h2 className="ml-3 text-lg font-bold text-white">
                Concept Visualizer
              </h2>
            </div>
            <p className="mt-3 text-sm text-indigo-200">
              Create and refine visual concepts with AI
            </p>
          </div>
          
          {/* Middle section - Feature links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase">
              Features
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link to="/create" className="text-sm text-indigo-200 hover:text-white transition-colors">
                  Create Concepts
                </Link>
              </li>
              <li>
                <Link to="/refine" className="text-sm text-indigo-200 hover:text-white transition-colors">
                  Refine Concepts
                </Link>
              </li>
              <li>
                <Link to="/gallery" className="text-sm text-indigo-200 hover:text-white transition-colors">
                  Concept Gallery
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Right section - Resources */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase">
              Resources
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <a 
                  href="https://github.com/username/concept-visualizer" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-sm text-indigo-200 hover:text-white transition-colors"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a 
                  href="https://jigsawstack.com" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-sm text-indigo-200 hover:text-white transition-colors"
                >
                  JigsawStack API
                </a>
              </li>
              <li>
                <a 
                  href="https://tailwindcss.com" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-sm text-indigo-200 hover:text-white transition-colors"
                >
                  Tailwind CSS
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Copyright */}
        <div className="mt-8 pt-4 border-t border-indigo-800 text-center">
          <p className="text-sm text-indigo-300">
            &copy; {year} Concept Visualizer. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}; 