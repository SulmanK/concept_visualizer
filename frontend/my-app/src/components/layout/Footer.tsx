import React from 'react';
import { Link } from 'react-router-dom';

export interface FooterProps {
  /**
   * Current year - defaults to current year
   */
  year?: number;
}

/**
 * Application footer with navigation, links and copyright
 * Uses dark indigo color scheme with responsive two-column layout
 */
export const Footer: React.FC<FooterProps> = ({ 
  year = new Date().getFullYear() 
}) => {
  return (
    <footer className="w-full bg-indigo-900 text-indigo-100 py-12 mt-12 shadow-lg relative overflow-hidden">
      <div className="container max-w-7xl mx-auto px-6 lg:px-8">
        {/* Two-column grid layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          {/* Brand column - takes up 1/3 of the space */}
          <div className="flex flex-col md:col-span-1">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-primary to-primary-dark rounded-lg flex items-center justify-center text-white font-bold shadow-md">
                CV
              </div>
              <h2 className="ml-3 text-xl font-bold text-white">
                Concept Visualizer
              </h2>
            </div>
            
            <p className="mt-4 text-sm text-indigo-200 leading-relaxed">
              Create and refine visual concepts with AI. Generate unique logos, color schemes, and design assets for your brand and projects.
            </p>
            
            <div className="mt-6">
              <a href="https://jigsawstack.com/?ref=powered-by" rel="follow" className="block">
                <img
                  src="https://jigsawstack.com/badge.svg"
                  alt="Powered by JigsawStack. The One API for your next big thing."
                  className="h-10 max-w-full"
                />
              </a>
            </div>
          </div>
          
          {/* Links grid - takes up 2/3 of the space */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 md:col-span-2">
            {/* Features column */}
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-white pb-2 mb-3 border-b border-indigo-700">
                Features
              </h3>
              <ul className="space-y-2">
                <li>
                  <Link 
                    to="/create" 
                    className="text-sm text-indigo-200 hover:text-white transition-colors duration-200 flex items-center group"
                  >
                    <svg className="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span className="relative">
                      Create Concepts
                      <span className="absolute bottom-0 left-0 w-0 h-px bg-white transition-all duration-200 group-hover:w-full"></span>
                    </span>
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/recent" 
                    className="text-sm text-indigo-200 hover:text-white transition-colors duration-200 flex items-center group"
                  >
                    <svg className="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="relative">
                      Recent Concepts
                      <span className="absolute bottom-0 left-0 w-0 h-px bg-white transition-all duration-200 group-hover:w-full"></span>
                    </span>
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/refine" 
                    className="text-sm text-indigo-200 hover:text-white transition-colors duration-200 flex items-center group"
                  >
                    <svg className="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                    <span className="relative">
                      Refine Concepts
                      <span className="absolute bottom-0 left-0 w-0 h-px bg-white transition-all duration-200 group-hover:w-full"></span>
                    </span>
                  </Link>
                </li>
              </ul>
            </div>
            
            {/* Resources column */}
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-white pb-2 mb-3 border-b border-indigo-700">
                Resources
              </h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="https://github.com/SulmanK/concept-visualizer"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-indigo-200 hover:text-white transition-colors duration-200 flex items-center group"
                  >
                    <svg className="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                    </svg>
                    <span className="relative">
                      GitHub Repository
                      <span className="absolute bottom-0 left-0 w-0 h-px bg-white transition-all duration-200 group-hover:w-full"></span>
                    </span>
                  </a>
                </li>
                <li>
                  <a
                    href="https://jigsawstack.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-indigo-200 hover:text-white transition-colors duration-200 flex items-center group"
                  >
                    <svg className="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span className="relative">
                      JigsawStack API
                      <span className="absolute bottom-0 left-0 w-0 h-px bg-white transition-all duration-200 group-hover:w-full"></span>
                    </span>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Footer bottom with copyright and GitHub link */}
        <div className="mt-10 pt-6 border-t border-indigo-700 flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
          <div className="text-xs text-indigo-300">
            &copy; {year} Concept Visualizer. All rights reserved.
          </div>
          
          <a
            href="https://github.com/SulmanK/concept-visualizer"
            className="w-8 h-8 flex items-center justify-center rounded-full bg-indigo-800/30 text-indigo-200 hover:bg-indigo-700/50 hover:text-white transition-all transform hover:-translate-y-1 hover:shadow-md"
            aria-label="GitHub"
            target="_blank"
            rel="noopener noreferrer"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
          </a>
        </div>
      </div>
    </footer>
  );
}; 

// Add default export to fix import issue
export default Footer;