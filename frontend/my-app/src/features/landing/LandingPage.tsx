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
 * Main landing page component for the application
 */
export const LandingPage: React.FC = () => {
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
  
  const handleEdit = (conceptId: string, variationIndex: number = 0) => {
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      alert('This is a sample concept. Please generate a real concept to edit it.');
      return;
    }
    
    // Find the concept
    const concept = recentConcepts.find(c => c.id === conceptId);
    if (!concept) {
      navigate(`/refine/${conceptId}`);
      return;
    }
    
    // Get the variation ID if available
    const variation = concept.color_variations && 
                      variationIndex < concept.color_variations.length ? 
                      concept.color_variations[variationIndex] : null;
    
    // If we have a variation, use its ID, otherwise just use the concept ID
    const variationId = variation ? variation.id : null;
    
    // Navigate to the refine page with variation ID as query parameter if available
    if (variationId) {
      navigate(`/refine/${conceptId}?colorId=${variationId}`);
    } else {
      navigate(`/refine/${conceptId}`);
    }
  };
  
  const handleViewDetails = (conceptId: string) => {
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      alert('This is a sample concept. Please generate a real concept to view details.');
      return;
    }
    navigate(`/concepts/${conceptId}`);
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
      
      // Get color variations - each variation has its own set of colors
      // This creates a 2D array where each inner array represents a color variation
      const colorVariations = concept.color_variations?.map(variation => variation.colors) || [];
      
      // If no color variations, provide a fallback
      if (colorVariations.length === 0) {
        colorVariations.push(['#4F46E5', '#60A5FA', '#1E293B']); // Fallback colors
      }
      
      // Get images from color variations
      const images = concept.color_variations?.map(variation => variation.image_url) || [];
      
      // Include original image for proper selection and display
      const originalImage = concept.base_image_url || '';
      
      return {
        id: concept.id,
        title: concept.logo_description.length > 20 
          ? `${concept.logo_description.substring(0, 20)}...` 
          : concept.logo_description,
        description: concept.theme_description.length > 40
          ? `${concept.theme_description.substring(0, 40)}...`
          : concept.theme_description,
        colorVariations,
        gradient: { from: 'blue-400', to: 'indigo-500' },
        initials,
        images,
        originalImage // Pass the original image separately
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
      colorVariations: [
        ['#4F46E5', '#60A5FA', '#1E293B'], 
        ['#1E40AF', '#93C5FD', '#0F172A']
      ],
      gradient: { from: 'blue-400', to: 'indigo-500' },
      initials: 'TC',
      images: ['/samples/tech-company.png'],
      originalImage: '/samples/tech-company.png' // Include original image
    },
    {
      id: 'sample-fs',
      title: 'Fashion Studio',
      description: 'Elegant fashion brand with clean typography',
      colorVariations: [
        ['#7E22CE', '#818CF8', '#F9A8D4'],
        ['#6D28D9', '#A78BFA', '#F472B6']
      ],
      gradient: { from: 'indigo-400', to: 'purple-500' },
      initials: 'FS',
      images: ['/samples/fashion-studio.png'],
      originalImage: '/samples/fashion-studio.png' // Include original image
    },
    {
      id: 'sample-ep',
      title: 'Eco Product',
      description: 'Sustainable brand with natural elements',
      colorVariations: [
        ['#059669', '#60A5FA', '#10B981'],
        ['#047857', '#3B82F6', '#059669']
      ],
      gradient: { from: 'blue-400', to: 'teal-500' },
      initials: 'EP',
      images: ['/samples/eco-product.png'],
      originalImage: '/samples/eco-product.png' // Include original image
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