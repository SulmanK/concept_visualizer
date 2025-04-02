import React from 'react';
import { ConceptCard } from '../../../components/ui/ConceptCard';

interface ConceptData {
  id: string;
  title: string;
  description: string;
  colorVariations: string[][];
  gradient: {
    from: string;
    to: string;
  };
  initials: string;
  images?: string[];
  originalImage?: string;
}

interface RecentConceptsSectionProps {
  concepts: ConceptData[];
  onEdit: (conceptId: string, variationIndex: number) => void;
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
              colorVariations={concept.colorVariations}
              images={concept.originalImage 
                ? [concept.originalImage, ...(concept.images || [])] 
                : concept.images}
              gradient={concept.gradient}
              initials={concept.initials}
              includeOriginal={!!concept.originalImage}
              onEdit={(index) => {
                const adjustedIndex = concept.originalImage && index === 0 ? -1 : index - (concept.originalImage ? 1 : 0);
                onEdit(concept.id, adjustedIndex);
              }}
              onViewDetails={() => onViewDetails(concept.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}; 