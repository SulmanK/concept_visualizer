import React, { useState } from 'react';
import { ConceptForm } from '../components/concept/ConceptForm';
import { ConceptResult } from '../components/concept/ConceptResult';
import { ConceptCard } from '../components/ui/ConceptCard';
import { GenerationResponse } from '../types';
import { useConceptGeneration } from '../hooks/useConceptGeneration';
import { useNavigate } from 'react-router-dom';

/**
 * Feature component for generating new concepts
 */
export const ConceptGenerator: React.FC = () => {
  const navigate = useNavigate();
  const { 
    generateConcept, 
    resetGeneration, 
    status, 
    result, 
    error,
    isLoading
  } = useConceptGeneration();
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  // Sample recent concepts for display
  const recentConcepts = [
    {
      id: 'tc',
      title: 'Tech Company',
      description: 'Modern minimalist tech logo with abstract elements',
      colors: ['#4F46E5', '#60A5FA', '#1E293B'],
      gradient: { from: 'blue-400', to: 'indigo-500' },
      initials: 'TC',
    },
    {
      id: 'fs',
      title: 'Fashion Studio',
      description: 'Elegant fashion brand with clean typography',
      colors: ['#7E22CE', '#818CF8', '#F9A8D4'],
      gradient: { from: 'indigo-400', to: 'purple-500' },
      initials: 'FS',
    },
    {
      id: 'ep',
      title: 'Eco Product',
      description: 'Sustainable brand with natural elements',
      colors: ['#059669', '#60A5FA', '#10B981'],
      gradient: { from: 'blue-400', to: 'teal-500' },
      initials: 'EP',
    },
  ];
  
  const handleGenerateConcept = (logoDescription: string, themeDescription: string) => {
    generateConcept(logoDescription, themeDescription);
    setSelectedColor(null);
  };
  
  const handleReset = () => {
    resetGeneration();
    setSelectedColor(null);
  };
  
  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    
    // Copy color to clipboard
    navigator.clipboard.writeText(color)
      .then(() => {
        // Could show a toast notification here
        console.log(`Copied ${color} to clipboard`);
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  };
  
  const handleEdit = (conceptId: string) => {
    navigate(`/refine/${conceptId}`);
  };
  
  const handleViewDetails = (conceptId: string) => {
    navigate(`/concept/${conceptId}`);
  };
  
  const headerTextStyle = {
    color: '#6366F1', // Using indigo-500 for text color
    fontSize: '1rem',
    lineHeight: '1.5',
    marginBottom: '2rem' // Increased spacing before form
  };
  
  return (
    <div className="space-y-8">
      <div className="text-left mb-8">
        <h1 className="text-4xl font-bold text-indigo-900 mb-4">
          Create Visual Concepts
        </h1>
        <p style={headerTextStyle}>
          Describe your logo and theme to generate visual concepts. Our AI will create a logo design and color palette based on your descriptions.
        </p>
      </div>
      
      <ConceptForm
        onSubmit={handleGenerateConcept}
        status={status}
        error={error}
        onReset={handleReset}
      />
      
      {status === 'success' && result && (
        <div className="mt-8 pt-8 border-t border-indigo-100">
          <ConceptResult
            concept={result}
            onRefineRequest={() => {
              // This would navigate to the refinement page with the current concept
              console.log('Navigate to refinement with:', result.generationId);
            }}
            onColorSelect={(color) => handleColorSelect(color)}
          />
          
          {selectedColor && (
            <div className="mt-4 text-center text-sm text-indigo-600">
              <span className="bg-indigo-50 px-2 py-1 rounded font-mono">
                {selectedColor}
              </span>
              <span className="ml-2">
                copied to clipboard
              </span>
            </div>
          )}
        </div>
      )}

      <div className="mt-16">
        <h2 className="text-2xl font-bold text-indigo-900 mb-6">
          Recent Concepts
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recentConcepts.map((concept) => (
            <ConceptCard
              key={concept.id}
              title={concept.title}
              description={concept.description}
              colors={concept.colors}
              gradient={concept.gradient}
              initials={concept.initials}
              onEdit={() => handleEdit(concept.id)}
              onViewDetails={() => handleViewDetails(concept.id)}
            />
          ))}
        </div>
      </div>
      
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-indigo-900 mb-6">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">1</div>
            <h3 className="text-lg font-semibold text-indigo-900 mb-2">Describe Your Vision</h3>
            <p className="text-sm text-indigo-700">Provide detailed descriptions of your logo concept and color preferences.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">2</div>
            <h3 className="text-lg font-semibold text-indigo-900 mb-2">AI Generation</h3>
            <p className="text-sm text-indigo-700">Our AI processes your description and creates unique visual concepts.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">3</div>
            <h3 className="text-lg font-semibold text-indigo-900 mb-2">Refine & Download</h3>
            <p className="text-sm text-indigo-700">Refine the generated concepts and download your final designs.</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 