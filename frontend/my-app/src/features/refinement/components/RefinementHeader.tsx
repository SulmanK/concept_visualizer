import React from 'react';

/**
 * Header component for the Refinement page
 */
export const RefinementHeader: React.FC = () => {
  return (
    <div className="text-center mb-8">
      <h1 className="text-3xl font-bold text-dark-900 mb-2">
        Refine Your Concept
      </h1>
      <p className="text-dark-600 max-w-2xl mx-auto">
        Provide instructions to refine your existing concept. You can update the logo or theme description, or specify what aspects to preserve.
      </p>
    </div>
  );
}; 