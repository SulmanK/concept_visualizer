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
            <p className="mt-1 text-xs text-indigo-600">Be descriptive about style, symbols, and colors you want</p>
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
            <p className="mt-1 text-xs text-indigo-600">Describe mood, colors, and style of your brand</p>
            {validationErrors.theme && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.theme}</p>
            )}
          </div>
        </div>
        
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
            {error}
          </div>
        )}
        
        <div className="flex justify-end">
          <Button
            type="submit"
            disabled={isSubmitting || isSuccess}
            variant="primary"
            size="lg"
          >
            {isSubmitting ? 'Generating...' : 'Generate Concept'}
          </Button>
        </div>
      </form>
    </div>
  );
}; 