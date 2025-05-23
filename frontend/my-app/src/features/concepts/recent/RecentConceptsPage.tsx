import React from "react";
import { ConceptList } from "./components/ConceptList";
import { RecentConceptsHeader } from "./components/RecentConceptsHeader";

/**
 * Main page component for displaying recent concepts
 * The view all button is not needed here as this is already the full list view
 */
export const RecentConceptsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white space-y-8">
      <RecentConceptsHeader />

      <main className="container mx-auto px-4 pt-4 pb-8 space-y-8">
        <ConceptList hideViewAllButton={true} />
      </main>
    </div>
  );
};
