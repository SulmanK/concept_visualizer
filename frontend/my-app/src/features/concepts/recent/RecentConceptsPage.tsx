import React from 'react';
import { ConceptList } from './components/ConceptList';
import { RecentConceptsHeader } from './components/RecentConceptsHeader';

/**
 * Main page component for displaying recent concepts
 */
export const RecentConceptsPage: React.FC = () => {
  return (
    <div className="space-y-8 relative">
      {/* Subtle background gradient for professional look */}
      <div className="absolute inset-0 bg-gradient-to-b from-indigo-50/50 to-white/70 -z-10" />
      
      <RecentConceptsHeader />
      
      {/* Add max-width for better readability on wide screens */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ConceptList />
      </div>
    </div>
  );
}; 