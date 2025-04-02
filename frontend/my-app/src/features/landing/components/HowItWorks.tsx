import React from 'react';
import { Button } from '../../../components/ui/Button';
import { HowItWorksProps } from '../types';

/**
 * HowItWorks component showing the 3-step process without connecting arrows
 */
export const HowItWorks: React.FC<HowItWorksProps> = ({ 
  steps, 
  onGetStarted 
}) => {
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-8 mb-12">
      <h2 className="text-2xl font-bold text-indigo-900 mb-16">How It Works</h2>
      
      {/* Steps grid without arrows */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-8 mt-8">
        {/* Steps with modern styling */}
        {steps.map((step) => (
          <div key={step.number} className="relative z-10 group">
            <div className="transition-all duration-300 p-5 rounded-lg hover:shadow-md bg-white border border-indigo-50">
              {/* Circle with number */}
              <div className="w-[70px] h-[70px] bg-gradient-to-r from-indigo-100 to-indigo-50 text-indigo-600 rounded-full flex items-center justify-center text-xl font-semibold mx-auto shadow-sm group-hover:shadow transition-all duration-300">
                {step.number}
              </div>
              
              {/* Title with consistent spacing */}
              <h3 className="text-lg font-semibold text-indigo-900 mt-5 mb-3 text-center">{step.title}</h3>
              
              {/* Separator line for visual hierarchy */}
              <div className="h-0.5 w-16 mx-auto bg-gradient-to-r from-indigo-200 to-indigo-100 rounded mb-4"></div>
              
              {/* Description with improved readability */}
              <p className="text-base text-indigo-800 leading-relaxed text-center px-2">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
      
      {/* Call to action */}
      <div className="text-center mt-10">
        <Button 
          variant="primary" 
          onClick={onGetStarted}
          size="lg"
          className="px-8 py-3 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5"
        >
          <span className="mr-2">✨</span>
          Get Started
        </Button>
      </div>
    </div>
  );
}; 