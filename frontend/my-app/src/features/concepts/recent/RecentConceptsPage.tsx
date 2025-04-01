import React from 'react';
import { ConceptList } from './components/ConceptList';
import { RecentConceptsHeader } from './components/RecentConceptsHeader';

/**
 * Main page component for displaying recent concepts
 */
export const RecentConceptsPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <RecentConceptsHeader />
      <ConceptList />
    </div>
  );
}; 