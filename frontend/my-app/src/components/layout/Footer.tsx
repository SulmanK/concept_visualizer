import React from 'react';

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
    <footer className="bg-dark-950 text-dark-100 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Left section */}
          <div>
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-primary rounded-full flex items-center justify-center text-white font-bold shadow-glow">
                CV
              </div>
              <h2 className="ml-3 text-lg font-semibold text-white">
                Concept Visualizer
              </h2>
            </div>
            <p className="mt-2 text-sm text-dark-300">
              Create and refine visual concepts with AI
            </p>
          </div>
          
          {/* Middle section - Feature links */}
          <div>
            <h3 className="text-sm font-semibold text-dark-100 tracking-wider uppercase">
              Features
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <a href="/" className="text-sm text-dark-300 hover:text-primary-400">
                  Create Concepts
                </a>
              </li>
              <li>
                <a href="/refine" className="text-sm text-dark-300 hover:text-primary-400">
                  Refine Concepts
                </a>
              </li>
              <li>
                <a href="/gallery" className="text-sm text-dark-300 hover:text-primary-400">
                  Concept Gallery
                </a>
              </li>
            </ul>
          </div>
          
          {/* Right section - Resources */}
          <div>
            <h3 className="text-sm font-semibold text-dark-100 tracking-wider uppercase">
              Resources
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <a 
                  href="https://github.com/username/concept-visualizer" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-sm text-dark-300 hover:text-primary-400"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a 
                  href="https://jigsawstack.com" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-sm text-dark-300 hover:text-primary-400"
                >
                  JigsawStack API
                </a>
              </li>
              <li>
                <a 
                  href="https://tailwindcss.com" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-sm text-dark-300 hover:text-primary-400"
                >
                  Tailwind CSS
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Copyright */}
        <div className="mt-8 pt-4 border-t border-dark-800 text-center">
          <p className="text-sm text-dark-400">
            &copy; {year} Concept Visualizer. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}; 