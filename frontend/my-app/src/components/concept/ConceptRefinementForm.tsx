import React, { useState, FormEvent } from 'react';
import { Button } from '../ui/Button';
import { TextArea } from '../ui/TextArea';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { FormStatus } from '../../types';

export interface ConceptRefinementFormProps {
  /**
   * Original image URL
   */
  originalImageUrl: string;
  
  /**
   * Handle form submission
   */
  onSubmit: (refinementPrompt: string, logoDescription: string, themeDescription: string, preserveAspects: string[]) => void;
  
  /**
   * Form submission status
   */
  status: FormStatus;
  
  /**
   * Error message from submission
   */
  error?: string | null;
  
  /**
   * Cancel refinement
   */
  onCancel?: () => void;
  
  /**
   * Initial logo description
   */
  initialLogoDescription?: string;
  
  /**
   * Initial theme description
   */
  initialThemeDescription?: string;
}

/**
 * Form for submitting concept refinement requests
 */
export const ConceptRefinementForm: React.FC<ConceptRefinementFormProps> = ({
  originalImageUrl,
  onSubmit,
  status,
  error,
  onCancel,
  initialLogoDescription = '',
  initialThemeDescription = '',
}) => {
  const [refinementPrompt, setRefinementPrompt] = useState('');
  const [logoDescription, setLogoDescription] = useState(initialLogoDescription);
  const [themeDescription, setThemeDescription] = useState(initialThemeDescription);
  const [preserveAspects, setPreserveAspects] = useState<string[]>([]);
  const [validationError, setValidationError] = useState<string | undefined>(undefined);
  
  const aspectOptions = [
    { id: 'layout', label: 'Layout' },
    { id: 'colors', label: 'Colors' },
    { id: 'style', label: 'Style' },
    { id: 'symbols', label: 'Symbols/Icons' },
    { id: 'proportions', label: 'Proportions' },
  ];
  
  const isSubmitting = status === 'submitting';
  const isSuccess = status === 'success';
  
  const validateForm = (): boolean => {
    if (!refinementPrompt.trim()) {
      setValidationError('Please provide refinement instructions');
      return false;
    }
    
    if (refinementPrompt.length < 5) {
      setValidationError('Refinement instructions must be at least 5 characters');
      return false;
    }
    
    setValidationError(undefined);
    return true;
  };
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(refinementPrompt, logoDescription, themeDescription, preserveAspects);
    }
  };
  
  const toggleAspect = (aspectId: string) => {
    setPreserveAspects(prev => 
      prev.includes(aspectId)
        ? prev.filter(id => id !== aspectId)
        : [...prev, aspectId]
    );
  };
  
  return (
    <Card 
      variant="gradient"
      className="max-w-xl mx-auto"
      header={
        <h2 className="text-xl font-semibold text-indigo-900">Refine Concept</h2>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Original image thumbnail */}
        <div className="flex justify-center mb-4">
          <div className="w-40 h-40 border border-indigo-200 rounded-lg overflow-hidden shadow-sm">
            <img 
              src={originalImageUrl} 
              alt="Original concept" 
              className="w-full h-full object-cover"
            />
          </div>
        </div>
        
        {/* Refinement instructions */}
        <div>
          <TextArea
            label="Refinement Instructions"
            placeholder="Describe how you want to refine this concept..."
            value={refinementPrompt}
            onChange={(e) => setRefinementPrompt(e.target.value)}
            error={validationError}
            fullWidth
            disabled={isSubmitting || isSuccess}
            helperText="Be specific about what you want to change"
            rows={3}
          />
        </div>
        
        {/* Optional: Updated logo description */}
        <div>
          <TextArea
            label="Updated Logo Description (Optional)"
            placeholder="Update the logo description or leave as is..."
            value={logoDescription}
            onChange={(e) => setLogoDescription(e.target.value)}
            fullWidth
            disabled={isSubmitting || isSuccess}
            helperText="Leave empty to keep original description"
            rows={2}
          />
        </div>
        
        {/* Optional: Updated theme description */}
        <div>
          <TextArea
            label="Updated Theme Description (Optional)"
            placeholder="Update the theme description or leave as is..."
            value={themeDescription}
            onChange={(e) => setThemeDescription(e.target.value)}
            fullWidth
            disabled={isSubmitting || isSuccess}
            helperText="Leave empty to keep original description"
            rows={2}
          />
        </div>
        
        {/* Preserve aspects checkboxes */}
        <div>
          <p className="block text-sm font-medium text-indigo-700 mb-2">Preserve Aspects (Optional)</p>
          <div className="flex flex-wrap gap-3">
            {aspectOptions.map(aspect => (
              <label 
                key={aspect.id}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={preserveAspects.includes(aspect.id)}
                  onChange={() => toggleAspect(aspect.id)}
                  disabled={isSubmitting || isSuccess}
                  className="rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4"
                />
                <span className="text-sm text-indigo-700">{aspect.label}</span>
              </label>
            ))}
          </div>
        </div>
        
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
            {error}
          </div>
        )}
        
        <div className="flex justify-end space-x-3 pt-2">
          {onCancel && (
            <Button
              variant="outline"
              onClick={onCancel}
              type="button"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}
          
          <Button
            variant="primary"
            type="submit"
            disabled={isSubmitting || isSuccess}
          >
            {isSubmitting ? 'Refining...' : 'Refine Concept'}
          </Button>
        </div>
      </form>
    </Card>
  );
}; 