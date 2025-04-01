import React from 'react';

/**
 * Header component for the Recent Concepts page
 */
export const RecentConceptsHeader: React.FC = () => {
  return (
    <div className="text-center mb-8">
      <h1 className="text-3xl font-bold text-indigo-900 mb-2">
        Your Recent Concepts
      </h1>
      <p className="text-indigo-600 max-w-2xl mx-auto">
        Browse your previously generated concepts and continue refining them to create the perfect visual identity.
      </p>
    </div>
  );
}; 