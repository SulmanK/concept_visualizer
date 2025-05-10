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

        <div className="inline-flex items-center bg-indigo-50 px-4 py-2 rounded-full border border-indigo-100 mt-2 mb-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4 mr-2 text-indigo-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span className="text-sm font-medium text-indigo-600">
            Concepts are automatically removed after 30 days
          </span>
        </div>
      </div>
    </div>
  );
};
