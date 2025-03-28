import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { ConceptCard } from '../components/ui/ConceptCard';
import { FeatureSteps } from '../components/ui/FeatureSteps';
import { ConceptForm } from '../components/concept/ConceptForm';
import { useConceptGeneration } from '../hooks/useConceptGeneration';
import { FormStatus } from '../types';
import { Card } from '../components/ui/Card';

/**
 * Home page feature component
 */
export const Home: React.FC = () => {
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
  
  const handleGenerateConcept = (logoDescription: string, themeDescription: string) => {
    generateConcept(logoDescription, themeDescription);
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
  
  const handleLearnMore = () => {
    // This could navigate to a documentation page
    console.log('Navigate to learn more page');
  };
  
  return (
    <div className="space-y-10 pb-12">
      {/* Hero section */}
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold text-indigo-900 mb-2">
          Create Visual Concepts
        </h1>
        <p className="text-indigo-600 max-w-2xl mx-auto text-sm">
          Describe your logo and theme to generate visual concepts. Our AI will create a logo design and color palette based on your descriptions.
        </p>
      </div>
      
      {/* Create New Concept Form */}
      <div id="create-form">
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-indigo-900 mb-6">Create New Concept</h3>
          
          <form className="space-y-6">
            {/* Logo Description */}
            <div>
              <label htmlFor="logo-description" className="label">
                Logo Description
              </label>
              <textarea 
                id="logo-description" 
                rows={4} 
                className="input"
                placeholder="Describe the logo you want to generate..."
              ></textarea>
              <p className="helper-text">Be descriptive about style, symbols, and colors you want</p>
            </div>
            
            {/* Theme Description */}
            <div>
              <label htmlFor="theme-description" className="label">
                Theme/Color Scheme Description
              </label>
              <textarea 
                id="theme-description" 
                rows={4} 
                className="input"
                placeholder="Describe the theme or color scheme..."
              ></textarea>
              <p className="helper-text">Describe mood, colors, and style of your brand</p>
            </div>
            
            {/* Submit Button */}
            <div className="flex justify-end">
              <Button variant="primary">
                Generate Concept
              </Button>
            </div>
          </form>
        </Card>
      </div>
      
      {/* Recent Concepts Grid */}
      <div>
        <h2 className="text-xl font-semibold text-indigo-900 mb-6">Recent Concepts</h2>
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
      
      {/* How It Works Section */}
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