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
  colorVariation?: {
    id: string;
    palette_name?: string;
    colors?: string[];
    description?: string;
  };
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
  colorVariation,
}) => {
  // Get placeholder text based on whether we're refining a color variation
  const getRefinementPlaceholder = () => {
    if (colorVariation) {
      return "Please refine this color variation by... e.g. 'Make the blue elements more prominent', 'Add more contrast', etc.";
    }
    return "Please refine this concept by... e.g. 'Make it more minimalist', 'Add more detail to the background', etc.";
  };

  // Get default preserve aspects based on whether we're refining a color variation
  const getDefaultPreserveAspects = () => {
    if (colorVariation) {
      return ['color_scheme'];
    }
    return [];
  };

  return (
    <ConceptRefinementForm
      originalImageUrl={originalImageUrl}
      onSubmit={onSubmit}
      status={status}
      error={error}
      onCancel={onCancel}
      initialLogoDescription={initialLogoDescription}
      initialThemeDescription={initialThemeDescription}
      refinementPlaceholder={getRefinementPlaceholder()}
      defaultPreserveAspects={getDefaultPreserveAspects()}
      isColorVariation={!!colorVariation}
      colorInfo={colorVariation?.colors ? {
        colors: colorVariation.colors,
        name: colorVariation.palette_name || 'Color Variation'
      } : undefined}
    />
  );
}; 