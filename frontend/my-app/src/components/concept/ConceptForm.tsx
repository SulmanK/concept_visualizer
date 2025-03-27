import React, { useState, FormEvent } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { TextArea } from '../ui/TextArea';
import { Card } from '../ui/Card';
import { FormStatus } from '../../types';

export interface ConceptFormProps {
  /**
   * Handle form submission
   */
  onSubmit: (logoDescription: string, themeDescription: string) => void;
  
  /**
   * Form submission status
   */
  status: FormStatus;
  
  /**
   * Error message from submission
   */
  error?: string | null;
  
  /**
   * Reset form and results
   */
  onReset?: () => void;
}

/**
 * Form for submitting concept generation requests
 */
export const ConceptForm: React.FC<ConceptFormProps> = ({
  onSubmit,
  status,
  error,
  onReset,
}) => {
  const [logoDescription, setLogoDescription] = useState('');
  const [themeDescription, setThemeDescription] = useState('');
  const [validationErrors, setValidationErrors] = useState<{
    logo?: string;
    theme?: string;
  }>({});
  
  const isSubmitting = status === 'submitting';
  const isSuccess = status === 'success';
  
  const validateForm = (): boolean => {
    const errors: { logo?: string; theme?: string } = {};
    
    if (!logoDescription.trim()) {
      errors.logo = 'Please enter a logo description';
    } else if (logoDescription.length < 5) {
      errors.logo = 'Logo description must be at least 5 characters';
    }
    
    if (!themeDescription.trim()) {
      errors.theme = 'Please enter a theme description';
    } else if (themeDescription.length < 5) {
      errors.theme = 'Theme description must be at least 5 characters';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(logoDescription, themeDescription);
    }
  };
  
  const handleReset = () => {
    setLogoDescription('');
    setThemeDescription('');
    setValidationErrors({});
    if (onReset) onReset();
  };
  
  return (
    <Card 
      variant="gradient"
      className="max-w-xl mx-auto"
      header={
        <h2 className="text-xl font-semibold text-dark-900">Create New Concept</h2>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <TextArea
            label="Logo Description"
            placeholder="Describe the logo you want to generate..."
            value={logoDescription}
            onChange={(e) => setLogoDescription(e.target.value)}
            error={validationErrors.logo}
            fullWidth
            disabled={isSubmitting || isSuccess}
            helperText="Be descriptive about style, symbols, and colors you want"
          />
        </div>
        
        <div>
          <TextArea
            label="Theme/Color Scheme Description"
            placeholder="Describe the theme or color scheme..."
            value={themeDescription}
            onChange={(e) => setThemeDescription(e.target.value)}
            error={validationErrors.theme}
            fullWidth
            disabled={isSubmitting || isSuccess}
            helperText="Describe mood, colors, and style of your brand"
          />
        </div>
        
        {error && (
          <div className="p-3 bg-accent-50 border border-accent-200 rounded text-accent-800 text-sm">
            {error}
          </div>
        )}
        
        <div className="flex justify-end space-x-3 pt-2">
          {isSuccess && (
            <Button
              variant="outline"
              onClick={handleReset}
              type="button"
            >
              Create New
            </Button>
          )}
          
          <Button
            variant="primary"
            type="submit"
            isLoading={isSubmitting}
            disabled={isSubmitting || isSuccess}
          >
            {isSubmitting ? 'Generating...' : 'Generate Concept'}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 