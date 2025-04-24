import React from "react";
import { Button } from "../../../components/ui/Button";

interface ConceptHeaderProps {
  onGetStarted: () => void;
}

/**
 * Header component for the landing page
 */
export const ConceptHeader: React.FC<ConceptHeaderProps> = ({
  onGetStarted,
}) => {
  return (
    <div className="py-12 sm:py-16 mb-8">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold text-indigo-900 mb-4">
          Create Visual Concepts
        </h1>
        <p className="text-indigo-700 text-lg sm:text-xl leading-relaxed mb-8 max-w-3xl mx-auto">
          Describe your logo and theme to generate visual concepts. Our AI will
          create a logo design and color palette based on your descriptions.
        </p>
        <Button
          variant="primary"
          size="lg"
          onClick={onGetStarted}
          className="shadow-lg hover:shadow-xl transition-all duration-300"
        >
          Get Started
        </Button>
      </div>
    </div>
  );
};
