import React from 'react';
import { ConceptCard } from '../../../components/ui/ConceptCard';

interface ConceptData {
  id: string;
  title: string;
  description: string;
  colors: string[];
  gradient: {
    from: string;
    to: string;
  };
  initials: string;
}

interface RecentConceptsSectionProps {
  concepts: ConceptData[];
  onEdit: (conceptId: string) => void;
  onViewDetails: (conceptId: string) => void;
}

/**
 * Recent concepts section showing previously created concepts
 */
export const RecentConceptsSection: React.FC<RecentConceptsSectionProps> = ({
  concepts,
  onEdit,
  onViewDetails
}) => {
  return (
    <div className="mt-16 mb-12">
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
        <h2 className="text-2xl font-bold text-indigo-900 mb-6">Recent Concepts</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {concepts.map((concept) => (
            <ConceptCard
              key={concept.id}
              title={concept.title}
              description={concept.description}
              colors={concept.colors}
              gradient={concept.gradient}
              initials={concept.initials}
              onEdit={() => onEdit(concept.id)}
              onViewDetails={() => onViewDetails(concept.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}; 