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
      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-8 mb-8">
        <h2 className="text-xl font-semibold text-indigo-900 mb-6">Create New Concept</h2>
        <ConceptForm 
          onSubmit={onSubmit}
          status={status}
          error={error}
          onReset={onReset}
        />
      </div>
    </div>
  );
}; 