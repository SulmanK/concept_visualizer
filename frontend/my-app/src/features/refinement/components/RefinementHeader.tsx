import React from 'react';

interface RefinementHeaderProps {
  /** Whether we're refining a color variation rather than the base concept */
  isVariation?: boolean;
  /** Name of the color variation being refined */
  variationName?: string;
}

/**
 * Header component for the Refinement page
 */
export const RefinementHeader: React.FC<RefinementHeaderProps> = ({ 
  isVariation = false,
  variationName
}) => {
  return (
    <div className="text-center mb-8">
      <h1 className="text-3xl font-bold text-dark-900 mb-2">
        Refine Your Concept
        {isVariation && variationName && (
          <span className="ml-2 text-indigo-600">
            ({variationName})
          </span>
        )}
      </h1>
      <p className="text-dark-600 max-w-2xl mx-auto">
        {isVariation 
          ? `You are refining a specific color variation of your concept. You can update the design while maintaining the color scheme.`
          : `Provide instructions to refine your existing concept. You can update the logo or theme description, or specify what aspects to preserve.`
        }
      </p>
    </div>
  );
}; 