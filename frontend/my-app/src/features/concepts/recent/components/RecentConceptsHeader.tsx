import React from "react";

/**
 * Header component for the Recent Concepts page
 * Styled to match the ConceptHeader on the landing page
 */
export const RecentConceptsHeader: React.FC = () => {
  return (
    <div className="py-12 sm:py-16 mb-8">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold text-indigo-900 mb-4">
          Your Recent Concepts
        </h1>
        <p className="text-indigo-700 text-lg sm:text-xl leading-relaxed mb-8 max-w-3xl mx-auto">
          Browse your previously generated concepts and continue refining them
          to create the perfect visual identity.
        </p>
      </div>
    </div>
  );
};
