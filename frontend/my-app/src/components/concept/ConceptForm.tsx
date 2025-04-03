import React, { useState, FormEvent, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { TextArea } from '../ui/TextArea';
import { Card } from '../ui/Card';
import { LoadingIndicator } from '../ui/LoadingIndicator';
import { ErrorMessage } from '../ui/ErrorMessage';
import { useToast } from '../../hooks/useToast';
import { useErrorHandling } from '../../hooks/useErrorHandling';
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
  
  const toast = useToast();
  const { setError, clearError, error: formError } = useErrorHandling();
  
  const isSubmitting = status === 'submitting';
  const isSuccess = status === 'success';
  
  // Handle external error props
  useEffect(() => {
    if (error) {
      setError(error, 'server');
    } else {
      clearError();
    }
  }, [error, setError, clearError]);
  
  // Show success toast when generation is complete
  useEffect(() => {
    if (status === 'success') {
      toast.showSuccess('Concept generated successfully!');
    }
  }, [status, toast]);
  
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
    
    // Show validation error toast if there are errors
    if (Object.keys(errors).length > 0) {
      toast.showWarning('Please fix the form errors before submitting.');
    }
    
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      toast.showInfo('Generating your concept...');
      onSubmit(logoDescription, themeDescription);
    }
  };
  
  const handleReset = () => {
    setLogoDescription('');
    setThemeDescription('');
    setValidationErrors({});
    clearError();
    if (onReset) onReset();
  };
  
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
      <h2 className="text-2xl font-bold text-indigo-900 mb-6">Create New Concept</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-indigo-700 mb-2">Logo Description</label>
            <textarea
              placeholder="Describe the logo you want to generate..."
              value={logoDescription}
              onChange={(e) => setLogoDescription(e.target.value)}
              className="w-full px-4 py-3 border border-indigo-200 rounded-lg bg-indigo-50/50 resize-y min-h-28 outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200"
              disabled={isSubmitting || isSuccess}
            />
            <p className="mt-1 text-xs text-indigo-600">
              <span className="font-medium">Pro tip:</span> "A minimalist fox logo with geometric shapes and clean lines" works better than "A cool fox logo"
            </p>
            {validationErrors.logo && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.logo}</p>
            )}
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-indigo-700 mb-2">Theme/Color Scheme Description</label>
            <textarea
              placeholder="Describe the theme or color scheme..."
              value={themeDescription}
              onChange={(e) => setThemeDescription(e.target.value)}
              className="w-full px-4 py-3 border border-indigo-200 rounded-lg bg-indigo-50/50 resize-y min-h-28 outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200"
              disabled={isSubmitting || isSuccess}
            />
            <p className="mt-1 text-xs text-indigo-600">
              <span className="font-medium">Pro tip:</span> "Energetic and playful with orange and blue tones, conveying creativity and trust" works better than "Bright and professional colors"
            </p>
            {validationErrors.theme && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.theme}</p>
            )}
          </div>
        </div>
        
        {formError && (
          <ErrorMessage 
            message={formError.message}
            details={formError.details}
            type={formError.category as any} 
            onDismiss={clearError}
            onRetry={isSubmitting ? undefined : () => validateForm() && onSubmit(logoDescription, themeDescription)}
          />
        )}
        
        <div className="flex justify-end items-center">
          {isSubmitting && (
            <div className="flex items-center mr-4">
              <LoadingIndicator size="small" showLabel labelText="Generating concept..." />
            </div>
          )}
          
          <Button
            type="submit"
            disabled={isSubmitting || isSuccess}
            variant="primary"
            size="lg"
          >
            {isSubmitting ? 'Please wait...' : 'Generate Concept'}
          </Button>
        </div>
      </form>
    </div>
  );
}; 