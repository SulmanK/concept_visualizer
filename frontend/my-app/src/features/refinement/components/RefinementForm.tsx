import React from 'react';
import { ConceptRefinementForm } from '../../../components/concept/ConceptRefinementForm';

interface RefinementFormProps {
  originalImageUrl: string;
  onSubmit: (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[]
  ) => void;
  status: 'idle' | 'loading' | 'success' | 'error';
  error?: string;
  onCancel: () => void;
  initialLogoDescription?: string;
  initialThemeDescription?: string;
}

/**
 * Form component for refining a concept
 */
export const RefinementForm: React.FC<RefinementFormProps> = ({
  originalImageUrl,
  onSubmit,
  status,
  error,
  onCancel,
  initialLogoDescription,
  initialThemeDescription,
}) => {
  return (
    <ConceptRefinementForm
      originalImageUrl={originalImageUrl}
      onSubmit={onSubmit}
      status={status}
      error={error}
      onCancel={onCancel}
      initialLogoDescription={initialLogoDescription}
      initialThemeDescription={initialThemeDescription}
    />
  );
}; 