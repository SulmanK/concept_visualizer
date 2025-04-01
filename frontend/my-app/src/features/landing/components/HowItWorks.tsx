import React from 'react';
import { Button } from '../../../components/ui/Button';
import { HowItWorksProps } from '../types';

/**
 * HowItWorks component showing the 3-step process with connecting arrows
 */
export const HowItWorks: React.FC<HowItWorksProps> = ({ 
  steps, 
  onGetStarted 
}) => {
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-8 mb-12">
      <h2 className="text-2xl font-bold text-indigo-900 mb-16">How It Works</h2>
      
      {/* Steps grid with connecting arrows */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 mt-8 relative">
        {/* Arrow from step 1 to 2 */}
        <div className="absolute top-8 left-[calc(16%+35px)] w-[calc(33.3%-70px)] h-0.5 bg-indigo-500 hidden md:block z-0">
          <div className="absolute -right-2 -top-1 w-0 h-0 border-t-[5px] border-b-[5px] border-l-[8px] border-solid border-t-transparent border-b-transparent border-l-indigo-500"></div>
        </div>
        
        {/* Arrow from step 2 to 3 */}
        <div className="absolute top-8 left-[calc(50%+35px)] w-[calc(33.3%-70px)] h-0.5 bg-indigo-500 hidden md:block z-0">
          <div className="absolute -right-2 -top-1 w-0 h-0 border-t-[5px] border-b-[5px] border-l-[8px] border-solid border-t-transparent border-b-transparent border-l-indigo-500"></div>
        </div>
        
        {/* Steps */}
        {steps.map((step) => (
          <div key={step.number} className="text-center relative z-10">
            <div className="w-[60px] h-[60px] bg-indigo-50 text-indigo-500 rounded-full flex items-center justify-center text-xl font-semibold mx-auto">
              {step.number}
            </div>
            <h3 className="text-lg font-semibold text-slate-800 my-4">{step.title}</h3>
            <p className="text-sm text-slate-600 leading-5">{step.description}</p>
          </div>
        ))}
      </div>
      
      {/* Call to action */}
      <div className="text-center mt-8">
        <Button 
          variant="primary" 
          onClick={onGetStarted}
          size="md"
        >
          Get Started
        </Button>
      </div>
    </div>
  );
}; 