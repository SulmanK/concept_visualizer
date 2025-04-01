import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConceptGeneration } from '../../hooks/useConceptGeneration';
import { ConceptHeader } from './components/ConceptHeader';
import { HowItWorks } from './components/HowItWorks';
import { ConceptFormSection } from './components/ConceptFormSection';
import { ResultsSection } from './components/ResultsSection';
import { RecentConceptsSection } from './components/RecentConceptsSection';

/**
 * Main page component for the Concept Generator feature
 */
export const ConceptGeneratorPage: React.FC = () => {
  const navigate = useNavigate();
  const { 
    generateConcept, 
    resetGeneration, 
    status, 
    result, 
    error 
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
  
  // Steps for how it works section
  const howItWorksSteps = [
    {
      number: 1,
      title: 'Describe Your Vision',
      description: 'Provide detailed descriptions of your logo concept and color preferences.',
    },
    {
      number: 2,
      title: 'AI Generation',
      description: 'Our AI processes your description and creates unique visual concepts.',
    },
    {
      number: 3,
      title: 'Refine & Download',
      description: 'Refine the generated concepts and download your final designs.',
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
  
  const handleGetStarted = () => {
    // Scroll to form
    const formElement = document.getElementById('create-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  return (
    <div className="space-y-12">
      <ConceptHeader />
      
      <HowItWorks 
        steps={howItWorksSteps} 
        onGetStarted={handleGetStarted} 
      />
      
      {result ? (
        <ResultsSection 
          result={result}
          onReset={handleReset}
          selectedColor={selectedColor}
          onColorSelect={handleColorSelect}
        />
      ) : (
        <ConceptFormSection 
          onSubmit={handleGenerateConcept}
          status={status}
          error={error}
          onReset={handleReset}
        />
      )}
      
      <RecentConceptsSection 
        concepts={recentConcepts}
        onEdit={handleEdit}
        onViewDetails={handleViewDetails}
      />
    </div>
  );
}; 