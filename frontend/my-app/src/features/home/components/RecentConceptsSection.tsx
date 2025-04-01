import React from 'react';
import { ConceptCard } from '../../../components/ui/ConceptCard';
import { Card } from '../../../components/ui/Card';

interface RecentConceptData {
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
  concepts: RecentConceptData[];
  onEdit: (conceptId: string) => void;
  onViewDetails: (conceptId: string) => void;
}

/**
 * Recent concepts section for the home page
 */
export const RecentConceptsSection: React.FC<RecentConceptsSectionProps> = ({
  concepts,
  onEdit,
  onViewDetails
}) => {
  return (
    <section className="mt-16">
      <Card className="p-8">
        <h2 className="text-xl font-semibold text-indigo-900 mb-12">Recent Concepts</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
      </Card>
    </section>
  );
}; 