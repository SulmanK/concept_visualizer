import React from 'react';
import { Card } from '../../../components/ui/Card';
import { ConceptForm } from '../../../components/concept/ConceptForm';
import { FormStatus } from '../../../types';

interface ConceptFormSectionProps {
  onSubmit: (logoDescription: string, themeDescription: string) => void;
  status: FormStatus;
  error: string | null;
  onReset: () => void;
}

/**
 * Concept form section for the home page
 */
export const ConceptFormSection: React.FC<ConceptFormSectionProps> = ({
  onSubmit,
  status,
  error,
  onReset
}) => {
  return (
    <section id="create-form">
      <Card>
        <ConceptForm 
          onSubmit={onSubmit}
          status={status}
          error={error}
          onReset={onReset}
        />
      </Card>
    </section>
  );
}; 