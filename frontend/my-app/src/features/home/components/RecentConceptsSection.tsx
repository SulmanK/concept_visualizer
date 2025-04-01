import React, { useEffect } from 'react';
import { ConceptData } from '../../../services/supabaseClient';
import { Card } from '../../../components/ui/Card';
import { HomeConceptCard } from './HomeConceptCard';

interface RecentConceptsSectionProps {
  concepts: ConceptData[];
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
  // Add debugging to see what concepts are being rendered
  useEffect(() => {
    console.log(`RecentConceptsSection received ${concepts.length} concepts`);
    
    if (concepts.length > 0) {
      concepts.forEach((concept, index) => {
        console.log(`Concept ${index + 1}:`, {
          id: concept.id,
          description: concept.logo_description,
          hasImage: !!concept.base_image_url, 
          imageUrl: concept.base_image_url,
          hasVariations: concept.color_variations && concept.color_variations.length > 0,
          variationsCount: concept.color_variations?.length || 0
        });
      });
    }
  }, [concepts]);
  
  return (
    <section className="mt-16">
      <Card className="p-8">
        <h2 className="text-xl font-semibold text-indigo-900 mb-12">Recent Concepts</h2>
        {concepts.length === 0 ? (
          <div className="text-center p-8">
            <p className="text-gray-500">No concepts available. Try generating some!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {concepts.map((concept) => (
              <HomeConceptCard
                key={concept.id}
                concept={concept}
                onEdit={() => onEdit(concept.id)}
                onViewDetails={() => onViewDetails(concept.id)}
              />
            ))}
          </div>
        )}
      </Card>
    </section>
  );
}; 