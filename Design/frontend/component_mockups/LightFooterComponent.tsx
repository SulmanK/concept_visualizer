import React from 'react';
import { Link } from 'react-router-dom';

export interface FooterProps {
  /**
   * Current year - defaults to current year
   */
  year?: number;
}

/**
 * Modern light-themed footer component with navigation, social links, and copyright
 */
export const LightFooter: React.FC<FooterProps> = ({ 
  year = new Date().getFullYear() 
}) => {
  return (
    <footer className="w-full bg-white border-t border-gray-200 shadow-sm py-12 mt-12 relative overflow-hidden">
      {/* Gradient top border */}
      <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-primary to-secondary"></div>
      
      {/* Subtle background decoration */}
      <div className="absolute bottom-0 right-0 w-[300px] h-[300px] bg-gradient-radial from-indigo-50/30 to-transparent pointer-events-none"></div>
      
      <div className="container max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        {/* Main footer content */}
        <div className="flex flex-col md:flex-row justify-between gap-10">
          {/* Left column */}
          <div className="flex flex-col max-w-xs">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-primary to-primary-dark rounded-lg flex items-center justify-center text-white font-bold shadow-modern">
                CV
              </div>
              <h2 className="ml-3 text-xl font-bold bg-gradient-to-r from-indigo-700 to-indigo-500 bg-clip-text text-transparent">
                Concept Visualizer
              </h2>
            </div>
            
            <p className="mt-4 text-sm text-gray-600 leading-relaxed">
              Create and refine visual concepts with AI. Generate unique logos, color schemes, and design assets for your brand and projects.
            </p>
            
            <a href="/get-started" className="mt-5 inline-flex items-center text-sm font-medium text-primary hover:text-primary-dark transition-colors duration-200">
              <span>Get Started</span>
              <svg className="ml-2 w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </a>
            
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
          
          {/* Right column with links grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 md:gap-12 lg:gap-16">
            {/* Features column */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-indigo-700 mb-4 pb-1 border-b border-indigo-100">
                Features
              </h3>
              <ul className="space-y-2">
                <li>
                  <Link 
                    to="/create" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Create Concepts
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/refine" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Refine Concepts
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/recent" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Recent Designs
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/export" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Export Options
                  </Link>
                </li>
              </ul>
            </div>
            
            {/* Resources column */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-indigo-700 mb-4 pb-1 border-b border-indigo-100">
                Resources
              </h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="https://github.com/username/concept-visualizer"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    GitHub Repository
                  </a>
                </li>
                <li>
                  <a
                    href="https://jigsawstack.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    JigsawStack API
                  </a>
                </li>
                <li>
                  <Link 
                    to="/docs" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Documentation
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/api" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    API Reference
                  </Link>
                </li>
              </ul>
            </div>
            
            {/* Company column */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-indigo-700 mb-4 pb-1 border-b border-indigo-100">
                Company
              </h3>
              <ul className="space-y-2">
                <li>
                  <Link 
                    to="/about" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    About Us
                  </Link>
                </li>
                <li>
                  <a
                    href="mailto:contact@example.com"
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Contact Us
                  </a>
                </li>
                <li>
                  <Link 
                    to="/privacy" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/terms" 
                    className="text-sm text-gray-600 hover:text-primary transition-colors duration-200"
                  >
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Divider */}
        <div className="h-px bg-gray-200 my-8"></div>
        
        {/* Footer bottom */}
        <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
          {/* Copyright */}
          <div className="text-xs text-gray-500">
            &copy; {year} Concept Visualizer. All rights reserved.
          </div>
          
          {/* Social links */}
          <div className="flex space-x-4">
            <a
              href="#"
              className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-primary rounded-full bg-gray-100 hover:bg-indigo-50 transition-all duration-200 transform hover:-translate-y-1"
              aria-label="Facebook"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
              </svg>
            </a>
            <a
              href="#"
              className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-primary rounded-full bg-gray-100 hover:bg-indigo-50 transition-all duration-200 transform hover:-translate-y-1"
              aria-label="Twitter"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a3.288 3.288 0 002.632 3.218 3.203 3.203 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
              </svg>
            </a>
            <a
              href="#"
              className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-primary rounded-full bg-gray-100 hover:bg-indigo-50 transition-all duration-200 transform hover:-translate-y-1"
              aria-label="GitHub"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
            </a>
            <a
              href="#"
              className="w-8 h-8 flex items-center justify-center text-gray-500 hover:text-primary rounded-full bg-gray-100 hover:bg-indigo-50 transition-all duration-200 transform hover:-translate-y-1"
              aria-label="LinkedIn"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M19.7 3H4.3A1.3 1.3 0 003 4.3v15.4A1.3 1.3 0 004.3 21h15.4a1.3 1.3 0 001.3-1.3V4.3A1.3 1.3 0 0019.7 3zM8.339 18.338H5.667v-8.59h2.672v8.59zM7.004 8.574a1.548 1.548 0 11-.002-3.096 1.548 1.548 0 01.002 3.096zm11.335 9.764H15.67v-4.177c0-.996-.017-2.278-1.387-2.278-1.389 0-1.601 1.086-1.601 2.206v4.249h-2.667v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.779 3.203 4.092v4.711z" clipRule="evenodd" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}; 