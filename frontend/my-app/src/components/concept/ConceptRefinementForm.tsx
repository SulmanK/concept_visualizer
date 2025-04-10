import React, { useState, FormEvent, useEffect } from 'react';
import { Button } from '../ui/Button';
import { TextArea } from '../ui/TextArea';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { FormStatus } from '../../types';
import { Spinner } from '../ui';

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

  /**
   * Custom placeholder text for refinement prompt
   */
  refinementPlaceholder?: string;

  /**
   * Default preserve aspects to pre-select
   */
  defaultPreserveAspects?: string[];

  /**
   * Whether we're refining a color variation
   */
  isColorVariation?: boolean;

  /**
   * Color information for the current variation
   */
  colorInfo?: {
    colors: string[];
    name: string;
  };

  /**
   * Whether the refinement request is being processed
   */
  isProcessing?: boolean;

  /**
   * Message to display during processing
   */
  processingMessage?: string;
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
  refinementPlaceholder = 'Describe how you want to refine this concept...',
  defaultPreserveAspects = [],
  isColorVariation = false,
  colorInfo,
  isProcessing = false,
  processingMessage = 'Processing your refinement request...',
}) => {
  const [refinementPrompt, setRefinementPrompt] = useState('');
  const [logoDescription, setLogoDescription] = useState(initialLogoDescription);
  const [themeDescription, setThemeDescription] = useState(initialThemeDescription);
  const [preserveAspects, setPreserveAspects] = useState<string[]>(defaultPreserveAspects);
  const [validationError, setValidationError] = useState<string | undefined>(undefined);
  
  // Update preserve aspects when defaultPreserveAspects changes
  useEffect(() => {
    setPreserveAspects(defaultPreserveAspects);
  }, [defaultPreserveAspects]);
  
  const aspectOptions = [
    { id: 'layout', label: 'Layout' },
    { id: 'colors', label: 'Colors' },
    { id: 'style', label: 'Style' },
    { id: 'symbols', label: 'Symbols/Icons' },
    { id: 'proportions', label: 'Proportions' },
    { id: 'color_scheme', label: 'Color Scheme' },
  ];
  
  const isSubmitting = status === 'submitting';
  const isSuccess = status === 'success';
  const formIsDisabled = isSubmitting || isSuccess || isProcessing;
  
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
        <h2 className="text-xl font-semibold text-indigo-900">
          Refine Concept
          {isColorVariation && colorInfo && (
            <span className="ml-2 text-sm font-normal text-indigo-600">
              ({colorInfo.name})
            </span>
          )}
        </h2>
      }
    >
      {isProcessing ? (
        <div className="py-8 flex flex-col items-center text-center">
          <Spinner size="lg" className="mb-4" />
          <p className="text-indigo-700 font-medium">{processingMessage}</p>
          <p className="text-sm text-indigo-500 mt-2">
            This might take a minute. Please wait while we process your request.
          </p>
        </div>
      ) : (
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
          
          {/* Color palette for variations */}
          {isColorVariation && colorInfo && colorInfo.colors.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-medium text-indigo-700 mb-2">Color Palette</p>
              <div className="flex flex-wrap gap-2">
                {colorInfo.colors.map((color, index) => (
                  <div 
                    key={index}
                    className="w-8 h-8 rounded-full border border-gray-200"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            </div>
          )}
          
          {/* Refinement instructions */}
          <div>
            <TextArea
              label="Refinement Instructions"
              placeholder={refinementPlaceholder}
              value={refinementPrompt}
              onChange={(e) => setRefinementPrompt(e.target.value)}
              error={validationError}
              fullWidth
              disabled={formIsDisabled}
              helperText={isColorVariation 
                ? "Describe what you want to change while keeping the color scheme" 
                : "Be specific about what you want to change"
              }
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
              disabled={formIsDisabled}
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
              disabled={formIsDisabled}
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
                    disabled={formIsDisabled || (isColorVariation && aspect.id === 'color_scheme')}
                    className="rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4"
                  />
                  <span className="text-sm text-indigo-700">{aspect.label}</span>
                </label>
              ))}
            </div>
          </div>
          
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
          
          <div className="flex items-center justify-end space-x-4 pt-4">
            {onCancel && (
              <Button 
                variant="ghost" 
                onClick={onCancel}
                disabled={formIsDisabled}
              >
                Cancel
              </Button>
            )}
            <Button 
              type="submit" 
              variant="primary"
              disabled={formIsDisabled}
            >
              {isSubmitting ? 'Submitting...' : 'Refine Concept'}
            </Button>
          </div>
        </form>
      )}
    </Card>
  );
}; 