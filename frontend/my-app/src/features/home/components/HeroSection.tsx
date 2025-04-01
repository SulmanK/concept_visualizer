import React from 'react';

/**
 * Hero section for the home page
 */
export const HeroSection: React.FC = () => {
  return (
    <section className="text-center mb-6">
      <h1 className="text-2xl font-bold text-indigo-900 mb-2">
        Create Visual Concepts
      </h1>
      <p className="text-indigo-600 max-w-2xl mx-auto text-sm">
        Describe your logo and theme to generate visual concepts. Our AI will create a logo design and color palette based on your descriptions.
      </p>
    </section>
  );
}; 