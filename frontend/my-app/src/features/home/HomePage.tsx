import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FeatureSteps } from '../../components/ui/FeatureSteps';
import { useConceptGeneration } from '../../hooks/useConceptGeneration';
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
  
  // Sample recent concepts for display
  const recentConcepts = [
    {
      id: 'tech-company',
      title: 'Tech Company',
      description: 'Modern minimalist tech logo with abstract elements',
      colors: ['#4F46E5', '#60A5FA', '#1E293B'],
      gradient: { from: 'blue-400', to: 'indigo-500' },
      initials: 'TC',
    },
    {
      id: 'fashion-studio',
      title: 'Fashion Studio',
      description: 'Elegant fashion brand with clean typography',
      colors: ['#7E22CE', '#818CF8', '#F9A8D4'],
      gradient: { from: 'indigo-400', to: 'purple-500' },
      initials: 'FS',
    },
    {
      id: 'eco-product',
      title: 'Eco Product',
      description: 'Sustainable brand with natural elements',
      colors: ['#059669', '#60A5FA', '#10B981'],
      gradient: { from: 'blue-400', to: 'teal-500' },
      initials: 'EP',
    },
  ];
  
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
  
  const handleLearnMore = () => {
    // This could navigate to a documentation page
    console.log('Navigate to learn more page');
  };
  
  return (
    <div className="space-y-10 pb-12">
      <HeroSection />
      
      <ConceptFormSection 
        onSubmit={generateConcept}
        status={status}
        error={error}
        onReset={resetGeneration}
      />
      
      <RecentConceptsSection 
        concepts={recentConcepts}
        onEdit={handleEdit}
        onViewDetails={handleViewDetails}
      />
      
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