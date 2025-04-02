import React from 'react';
import { Card } from './Card';
import { Button } from './Button';

export interface FeatureStep {
  /**
   * Step number (1, 2, 3, etc.)
   */
  number: number;
  
  /**
   * Step title
   */
  title: string;
  
  /**
   * Step description
   */
  description: string;
}

export interface FeatureStepsProps {
  /**
   * Section title
   */
  title: string;
  
  /**
   * Array of feature steps
   */
  steps: FeatureStep[];
  
  /**
   * Primary action button text
   */
  primaryActionText?: string;
  
  /**
   * Secondary action button text
   */
  secondaryActionText?: string;
  
  /**
   * Primary action handler
   */
  onPrimaryAction?: () => void;
  
  /**
   * Secondary action handler
   */
  onSecondaryAction?: () => void;
}

/**
 * Component for displaying a "How It Works" section with numbered steps
 */
export const FeatureSteps: React.FC<FeatureStepsProps> = ({
  title,
  steps,
  primaryActionText,
  secondaryActionText,
  onPrimaryAction,
  onSecondaryAction,
}) => {
  return (
    <div className="rounded-lg shadow-modern border border-indigo-100 bg-white/90 backdrop-blur-sm overflow-hidden p-6 fade-in">
      <h3 className="text-xl font-semibold text-indigo-900 mb-6">{title}</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {steps.map((step) => (
          <div key={step.number} className="text-center hover-lift">
            <div className="w-16 h-16 mx-auto bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 text-2xl mb-4 hover-bright transition-all duration-300">
              {step.number}
            </div>
            <h4 className="font-semibold text-lg text-indigo-900 mb-2">{step.title}</h4>
            <p className="text-gray-600">{step.description}</p>
          </div>
        ))}
      </div>
      
      {(primaryActionText || secondaryActionText) && (
        <div className="mt-8 text-center">
          {primaryActionText && (
            <Button
              variant="primary"
              onClick={onPrimaryAction}
              className="hover-lift"
            >
              {primaryActionText}
            </Button>
          )}
          
          {secondaryActionText && (
            <Button
              variant="outline"
              onClick={onSecondaryAction}
              className="ml-4 hover-lift"
            >
              {secondaryActionText}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default FeatureSteps; 