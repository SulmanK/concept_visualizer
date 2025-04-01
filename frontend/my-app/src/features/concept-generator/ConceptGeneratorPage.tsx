import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConceptGeneration } from '../../hooks/useConceptGeneration';
import { useConceptContext } from '../../contexts/ConceptContext';
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
  
  // Use the concept context to get real concepts
  const { recentConcepts, loadingConcepts, refreshConcepts } = useConceptContext();
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
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
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      alert('This is a sample concept. Please generate a real concept to edit it.');
      return;
    }
    navigate(`/refine/${conceptId}`);
  };
  
  const handleViewDetails = (conceptId: string) => {
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      alert('This is a sample concept. Please generate a real concept to view details.');
      return;
    }
    navigate(`/concept/${conceptId}`);
  };
  
  const handleGetStarted = () => {
    // Scroll to form
    const formElement = document.getElementById('create-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  // Transform the concept data for the RecentConceptsSection
  const formatConceptsForDisplay = () => {
    if (!recentConcepts || recentConcepts.length === 0) return [];
    
    return recentConcepts.slice(0, 3).map(concept => {
      // Get initials from the logo description
      const words = concept.logo_description.trim().split(/\s+/);
      const initials = words.length === 1 
        ? words[0].substring(0, 2).toUpperCase()
        : (words[0][0] + words[1][0]).toUpperCase();
      
      // Get colors from the first color variation if available
      const colors = concept.color_variations && concept.color_variations.length > 0
        ? concept.color_variations[0].colors.slice(0, 3)
        : ['#4F46E5', '#60A5FA', '#1E293B']; // Fallback colors
      
      return {
        id: concept.id,
        title: concept.logo_description.length > 20 
          ? `${concept.logo_description.substring(0, 20)}...` 
          : concept.logo_description,
        description: concept.theme_description.length > 40
          ? `${concept.theme_description.substring(0, 40)}...`
          : concept.theme_description,
        colors,
        gradient: { from: 'blue-400', to: 'indigo-500' },
        initials
      };
    });
  };
  
  // Format the concepts for display
  const formattedConcepts = formatConceptsForDisplay();
  
  // Sample concepts to use when no real concepts are available
  const sampleConcepts = [
    {
      id: 'sample-tc',
      title: 'Tech Company',
      description: 'Modern minimalist tech logo with abstract elements',
      colors: ['#4F46E5', '#60A5FA', '#1E293B'],
      gradient: { from: 'blue-400', to: 'indigo-500' },
      initials: 'TC',
    },
    {
      id: 'sample-fs',
      title: 'Fashion Studio',
      description: 'Elegant fashion brand with clean typography',
      colors: ['#7E22CE', '#818CF8', '#F9A8D4'],
      gradient: { from: 'indigo-400', to: 'purple-500' },
      initials: 'FS',
    },
    {
      id: 'sample-ep',
      title: 'Eco Product',
      description: 'Sustainable brand with natural elements',
      colors: ['#059669', '#60A5FA', '#10B981'],
      gradient: { from: 'blue-400', to: 'teal-500' },
      initials: 'EP',
    },
  ];
  
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
      
      {/* Show real concepts if available, otherwise show sample concepts */}
      {!loadingConcepts && (
        formattedConcepts.length > 0 ? (
          <RecentConceptsSection 
            concepts={formattedConcepts}
            onEdit={handleEdit}
            onViewDetails={handleViewDetails}
          />
        ) : (
          <RecentConceptsSection 
            concepts={sampleConcepts}
            onEdit={handleEdit}
            onViewDetails={handleViewDetails}
          />
        )
      )}
    </div>
  );
}; 