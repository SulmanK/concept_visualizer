import React from 'react';
import { Button } from '../../../components/ui/Button';
import { HowItWorksProps } from '../types';

/**
 * HowItWorks component showing the 3-step process
 * Optimized for both mobile and desktop viewing
 */
export const HowItWorks: React.FC<HowItWorksProps> = ({ 
  steps, 
  onGetStarted 
}) => {
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-4 sm:p-6 md:p-8 mb-8 sm:mb-12">
      <h2 className="text-xl sm:text-2xl font-bold text-indigo-900 mb-8 sm:mb-16 text-center sm:text-left">How It Works</h2>
      
      {/* Steps grid - vertical on mobile, horizontal on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 md:gap-10 mb-6 sm:mb-8">
        {/* Steps with modern styling */}
        {steps.map((step) => (
          <div key={step.number} className="relative z-10 group">
            <div className="transition-all duration-300 p-4 sm:p-5 rounded-lg hover:shadow-md bg-white border border-indigo-50 flex flex-col items-center">
              {/* Circle with number */}
              <div className="w-[50px] h-[50px] sm:w-[70px] sm:h-[70px] bg-gradient-to-r from-indigo-100 to-indigo-50 text-indigo-600 rounded-full flex items-center justify-center text-lg sm:text-xl font-semibold mx-auto shadow-sm group-hover:shadow transition-all duration-300">
                {step.number}
              </div>
              
              {/* Title with consistent spacing */}
              <h3 className="text-base sm:text-lg font-semibold text-indigo-900 mt-4 sm:mt-5 mb-2 sm:mb-3 text-center">{step.title}</h3>
              
              {/* Separator line for visual hierarchy */}
              <div className="h-0.5 w-12 sm:w-16 mx-auto bg-gradient-to-r from-indigo-200 to-indigo-100 rounded mb-3 sm:mb-4"></div>
              
              {/* Description with improved readability */}
              <p className="text-sm sm:text-base text-indigo-800 leading-relaxed text-center px-1 sm:px-2">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
      
      {/* Call to action */}
      <div className="text-center mt-6 sm:mt-10">
        <Button 
          variant="primary" 
          onClick={onGetStarted}
          size="lg"
          className="px-6 sm:px-8 py-2.5 sm:py-3 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 w-full sm:w-auto"
        >
          <span className="mr-2">✨</span>
          Get Started
        </Button>
      </div>
    </div>
  );
}; 