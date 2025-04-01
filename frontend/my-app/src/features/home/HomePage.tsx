import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FeatureSteps } from '../../components/ui/FeatureSteps';
import { useConceptGeneration } from '../../hooks/useConceptGeneration';
import { useConceptContext } from '../../contexts/ConceptContext';
import { ConceptData } from '../../services/supabaseClient';
import { HeroSection } from './components/HeroSection';
import { ConceptFormSection } from './components/ConceptFormSection';
import { RecentConceptsSection } from './components/RecentConceptsSection';

/**
 * Home page feature component
 */
export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { 
    generateConcept, 
    resetGeneration, 
    status, 
    error 
  } = useConceptGeneration();
  
  // Use the concept context to get real concepts
  const { recentConcepts, loadingConcepts, refreshConcepts } = useConceptContext();
  
  // Add debug logging to see what concepts are available
  useEffect(() => {
    console.log(`HomePage: recentConcepts length = ${recentConcepts.length}`);
    if (recentConcepts.length > 0) {
      console.log('First concept:', {
        id: recentConcepts[0].id,
        logo_description: recentConcepts[0].logo_description,
        hasVariations: recentConcepts[0].color_variations && recentConcepts[0].color_variations.length > 0,
        image: recentConcepts[0].base_image_url
      });
    }
  }, [recentConcepts]);
  
  // Fetch concepts on component mount
  useEffect(() => {
    console.log('HomePage: refreshing concepts');
    refreshConcepts()
      .then(() => console.log('HomePage: refreshConcepts completed'))
      .catch(err => console.error('HomePage: error refreshing concepts', err));
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // How it works steps
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
    navigate(`/concepts/${conceptId}`);
  };
  
  const handleGetStarted = () => {
    // Scroll to form
    const formElement = document.getElementById('create-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  const handleLearnMore = () => {
    // This could navigate to a documentation page
    console.log('Navigate to learn more page');
  };
  
  // Sample concepts to display when no real concepts are available
  const sampleConcepts: ConceptData[] = [
    {
      id: 'sample-tc',
      session_id: 'sample-session',
      logo_description: 'Modern minimalist tech logo with abstract elements',
      theme_description: 'A clean, modern design for a technology company with a focus on innovation.',
      base_image_path: '/sample-images/tech-logo.png',
      base_image_url: '/sample-images/tech-logo.png',
      created_at: new Date().toISOString(),
      color_variations: [
        {
          id: 'sample-tc-1',
          concept_id: 'sample-tc',
          palette_name: 'Blue Tech',
          colors: ['#4F46E5', '#60A5FA', '#1E293B', '#F8FAFC', '#0F172A'],
          description: 'Blue color scheme for a professional tech look',
          image_path: '/sample-images/tech-logo-blue.png',
          image_url: '/sample-images/tech-logo-blue.png',
          created_at: new Date().toISOString()
        },
        {
          id: 'sample-tc-2',
          concept_id: 'sample-tc',
          palette_name: 'Deep Blue',
          colors: ['#4338CA', '#6366F1', '#312E81', '#F8FAFC', '#1E1B4B'],
          description: 'Deep blue color scheme for a more serious tone',
          image_path: '/sample-images/tech-logo-deep-blue.png',
          image_url: '/sample-images/tech-logo-deep-blue.png',
          created_at: new Date().toISOString()
        },
        {
          id: 'sample-tc-3',
          concept_id: 'sample-tc',
          palette_name: 'Navy Blue',
          colors: ['#1E40AF', '#3B82F6', '#1E3A8A', '#F8FAFC', '#172554'],
          description: 'Navy blue color scheme for a corporate feel',
          image_path: '/sample-images/tech-logo-navy.png',
          image_url: '/sample-images/tech-logo-navy.png',
          created_at: new Date().toISOString()
        }
      ]
    },
    {
      id: 'sample-fs',
      session_id: 'sample-session',
      logo_description: 'Elegant fashion brand with clean typography',
      theme_description: 'A sophisticated and elegant design for a high-end fashion brand.',
      base_image_path: '/sample-images/fashion-logo.png',
      base_image_url: '/sample-images/fashion-logo.png',
      created_at: new Date().toISOString(),
      color_variations: [
        {
          id: 'sample-fs-1',
          concept_id: 'sample-fs',
          palette_name: 'Purple Elegance',
          colors: ['#7E22CE', '#818CF8', '#F9A8D4', '#FDF2F8', '#4A044E'],
          description: 'Purple color scheme for a luxurious feel',
          image_path: '/sample-images/fashion-logo-purple.png',
          image_url: '/sample-images/fashion-logo-purple.png',
          created_at: new Date().toISOString()
        },
        {
          id: 'sample-fs-2',
          concept_id: 'sample-fs',
          palette_name: 'Lavender',
          colors: ['#6D28D9', '#A78BFA', '#F472B6', '#FDF2F8', '#581C87'],
          description: 'Lavender color scheme for a softer, feminine aesthetic',
          image_path: '/sample-images/fashion-logo-lavender.png',
          image_url: '/sample-images/fashion-logo-lavender.png',
          created_at: new Date().toISOString()
        },
        {
          id: 'sample-fs-3',
          concept_id: 'sample-fs',
          palette_name: 'Royal Purple',
          colors: ['#5B21B6', '#8B5CF6', '#F87171', '#FEF2F2', '#3B0764'],
          description: 'Royal purple color scheme for a bold, high-end look',
          image_path: '/sample-images/fashion-logo-royal.png',
          image_url: '/sample-images/fashion-logo-royal.png',
          created_at: new Date().toISOString()
        }
      ]
    },
    {
      id: 'sample-ep',
      session_id: 'sample-session',
      logo_description: 'Sustainable brand with natural elements',
      theme_description: 'An eco-friendly design for a sustainable product brand focused on environmental responsibility.',
      base_image_path: '/sample-images/eco-logo.png',
      base_image_url: '/sample-images/eco-logo.png',
      created_at: new Date().toISOString(),
      color_variations: [
        {
          id: 'sample-ep-1',
          concept_id: 'sample-ep',
          palette_name: 'Green Earth',
          colors: ['#059669', '#60A5FA', '#10B981', '#ECFDF5', '#064E3B'],
          description: 'Green color scheme for an eco-friendly brand',
          image_path: '/sample-images/eco-logo-green.png',
          image_url: '/sample-images/eco-logo-green.png',
          created_at: new Date().toISOString()
        },
        {
          id: 'sample-ep-2',
          concept_id: 'sample-ep',
          palette_name: 'Fresh Green',
          colors: ['#047857', '#38BDF8', '#34D399', '#ECFDF5', '#065F46'],
          description: 'Fresh green color scheme for a natural, organic feel',
          image_path: '/sample-images/eco-logo-fresh.png',
          image_url: '/sample-images/eco-logo-fresh.png',
          created_at: new Date().toISOString()
        },
        {
          id: 'sample-ep-3',
          concept_id: 'sample-ep',
          palette_name: 'Vibrant Green',
          colors: ['#065F46', '#0EA5E9', '#6EE7B7', '#ECFDF5', '#064E3B'],
          description: 'Vibrant green color scheme for an energetic, eco-conscious brand',
          image_path: '/sample-images/eco-logo-vibrant.png',
          image_url: '/sample-images/eco-logo-vibrant.png',
          created_at: new Date().toISOString()
        }
      ]
    }
  ];
  
  // Get the first 3 recent concepts for display
  const topThreeConcepts = recentConcepts.slice(0, 3);
  
  // Debug what we're actually showing
  useEffect(() => {
    console.log(`HomePage render - topThreeConcepts length: ${topThreeConcepts.length}`);
    console.log(`Will show sample concepts: ${topThreeConcepts.length === 0 && !loadingConcepts}`);
  }, [topThreeConcepts.length, loadingConcepts]);
  
  return (
    <div className="space-y-10 pb-12">
      <HeroSection />
      
      <ConceptFormSection 
        onSubmit={generateConcept}
        status={status}
        error={error}
        onReset={resetGeneration}
      />
      
      {/* Show real concepts if available, otherwise show sample concepts */}
      {!loadingConcepts && (
        <div>
          {/* Debug in useEffect, not in JSX */}
          {topThreeConcepts.length > 0 ? (
            <RecentConceptsSection 
              concepts={topThreeConcepts}
              onEdit={handleEdit}
              onViewDetails={handleViewDetails}
            />
          ) : (
            <RecentConceptsSection 
              concepts={sampleConcepts}
              onEdit={handleEdit}
              onViewDetails={handleViewDetails}
            />
          )}
        </div>
      )}
      
      <FeatureSteps
        title="How It Works"
        steps={howItWorksSteps}
        primaryActionText="Get Started"
        secondaryActionText="Learn More"
        onPrimaryAction={handleGetStarted}
        onSecondaryAction={handleLearnMore}
      />
    </div>
  );
}; 