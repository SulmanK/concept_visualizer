import React from 'react';
import { ConceptForm } from '../../../components/concept/ConceptForm';
import { FormStatus } from '../../../types';

interface ConceptFormSectionProps {
  id?: string;
  onSubmit: (logoDescription: string, themeDescription: string) => void;
  status: FormStatus;
  errorMessage: string | null;
  onReset?: () => void;
  isProcessing?: boolean;
  processingMessage?: string;
}

/**
 * Form section for the landing page
 * Optimized for responsive viewing on both mobile and desktop
 */
export const ConceptFormSection: React.FC<ConceptFormSectionProps> = ({
  id,
  onSubmit,
  status,
  errorMessage,
  onReset,
  isProcessing,
  processingMessage
}) => {
  return (
    <div id={id} className="mb-8 sm:mb-16">
      <ConceptForm 
        onSubmit={onSubmit}
        status={status}
        error={errorMessage}
        onReset={onReset}
        isProcessing={isProcessing}
        processingMessage={processingMessage}
      />
    </div>
  );
}; 