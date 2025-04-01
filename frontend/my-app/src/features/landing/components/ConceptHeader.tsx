import React from 'react';

/**
 * Header component for the landing page
 */
export const ConceptHeader: React.FC = () => {
  return (
    <div className="text-center mb-8">
      <h1 className="text-4xl font-bold text-indigo-900 mb-4">
        Create Visual Concepts
      </h1>
      <p className="text-indigo-500 text-base leading-relaxed mb-8 max-w-3xl mx-auto">
        Describe your logo and theme to generate visual concepts. Our AI will create a logo design and color palette based on your descriptions.
      </p>
    </div>
  );
}; 