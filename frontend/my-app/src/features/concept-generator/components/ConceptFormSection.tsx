import React from 'react';
import { ConceptForm } from '../../../components/concept/ConceptForm';
import { FormStatus } from '../../../types';

interface ConceptFormSectionProps {
  onSubmit: (logoDescription: string, themeDescription: string) => void;
  status: FormStatus;
  error: string | null;
  onReset?: () => void;
}

/**
 * Form section for the Concept Generator feature
 */
export const ConceptFormSection: React.FC<ConceptFormSectionProps> = ({
  onSubmit,
  status,
  error,
  onReset
}) => {
  return (
    <div id="create-form" className="mb-16">
      <ConceptForm 
        onSubmit={onSubmit}
        status={status}
        error={error}
        onReset={onReset}
      />
    </div>
  );
}; 