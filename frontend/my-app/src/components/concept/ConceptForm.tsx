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
  
  const formStyle = {
    backgroundColor: 'white',
    borderRadius: '0.75rem',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02)',
    padding: '2rem',
    marginBottom: '2rem'
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#4338CA',
    marginBottom: '0.5rem'
  };

  const inputStyle = {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #E0E7FF',
    borderRadius: '0.375rem',
    fontSize: '0.875rem',
    backgroundColor: '#F5F7FF',
    resize: 'vertical' as const,
    minHeight: '7rem',
    outline: 'none',
    transition: 'border-color 0.2s, box-shadow 0.2s'
  };

  const helperTextStyle = {
    fontSize: '0.75rem',
    color: '#6366F1',
    marginTop: '0.25rem'
  };

  const buttonStyle = {
    backgroundColor: '#4F46E5',
    color: 'white',
    padding: '0.75rem 1.5rem',
    borderRadius: '0.375rem',
    fontWeight: 600,
    border: 'none',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    marginTop: '1rem'
  };
  
  return (
    <div style={formStyle}>
      <h2 className="text-xl font-semibold text-indigo-900 mb-6">Create New Concept</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <div className="mb-6">
            <label style={labelStyle}>Logo Description</label>
            <textarea
              placeholder="Describe the logo you want to generate..."
              value={logoDescription}
              onChange={(e) => setLogoDescription(e.target.value)}
              style={inputStyle}
              disabled={isSubmitting || isSuccess}
            />
            <p style={helperTextStyle}>Be descriptive about style, symbols, and colors you want</p>
            {validationErrors.logo && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.logo}</p>
            )}
          </div>
          
          <div className="mb-6">
            <label style={labelStyle}>Theme/Color Scheme Description</label>
            <textarea
              placeholder="Describe the theme or color scheme..."
              value={themeDescription}
              onChange={(e) => setThemeDescription(e.target.value)}
              style={inputStyle}
              disabled={isSubmitting || isSuccess}
            />
            <p style={helperTextStyle}>Describe mood, colors, and style of your brand</p>
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
          <button
            type="submit"
            style={buttonStyle}
            disabled={isSubmitting || isSuccess}
          >
            {isSubmitting ? 'Generating...' : 'Generate Concept'}
          </button>
        </div>
      </form>
    </div>
  );
}; 