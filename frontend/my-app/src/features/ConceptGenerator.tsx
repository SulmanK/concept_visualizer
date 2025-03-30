import React, { useState } from 'react';
import { ConceptForm } from '../components/concept/ConceptForm';
import { ConceptResult } from '../components/concept/ConceptResult';
import { ConceptCard } from '../components/ui/ConceptCard';
import { GenerationResponse } from '../types';
import { useConceptGeneration } from '../hooks/useConceptGeneration';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';

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
  
  const cardStyle = {
    backgroundColor: 'white',
    borderRadius: '0.75rem',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02)',
    padding: '2rem',
    marginBottom: '2rem'
  };
  
  const circleNumberStyle = {
    width: '48px', 
    height: '48px', 
    backgroundColor: '#EEF2FF', 
    color: '#4F46E5', 
    borderRadius: '50%', 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    fontSize: '20px', 
    fontWeight: 600
  };
  
  const editButtonStyle = {
    color: '#6366F1',
    fontWeight: 500,
    fontSize: '0.875rem',
    textDecoration: 'none',
    padding: '0',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    transition: 'color 0.2s ease'
  };
  
  const viewDetailsButtonStyle = {
    color: '#6366F1',
    fontWeight: 500,
    fontSize: '0.875rem',
    textDecoration: 'none',
    padding: '0',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    transition: 'color 0.2s ease'
  };
  
  const handleGetStarted = () => {
    // Scroll to form
    const formElement = document.getElementById('create-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  const conceptCardStyle = {
    display: 'flex',
    flexDirection: 'column' as const,
    backgroundColor: 'white',
    borderRadius: '0.5rem',
    overflow: 'hidden',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    height: '100%'
  };
  
  const conceptGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '2rem',
    margin: '0',
    padding: '0',
    width: '100%'
  };
  
  return (
    <div className="space-y-12">
      <div className="text-left mb-8">
        <h1 className="text-4xl font-bold text-indigo-900 mb-4">
          Create Visual Concepts
        </h1>
        <p style={headerTextStyle}>
          Describe your logo and theme to generate visual concepts. Our AI will create a logo design and color palette based on your descriptions.
        </p>
      </div>
      
      <div style={{...cardStyle, marginBottom: '3rem'}} className="mt-8">
        <h2 className="text-2xl font-bold text-indigo-900 mb-16">
          How It Works
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem', marginTop: '2rem', position: 'relative' }}>
          {/* Arrow 1 to 2 */}
          <div style={{
            position: 'absolute',
            top: '30px',
            left: 'calc(16.0% + 35px)',
            width: 'calc(33.3% - 70px)',
            height: '2px',
            backgroundColor: '#6366F1',
            zIndex: 0
          }}>
            <div style={{
              position: 'absolute',
              right: '-8px',
              top: '-4px',
              width: '0',
              height: '0',
              borderTop: '5px solid transparent',
              borderBottom: '5px solid transparent',
              borderLeft: '8px solid #6366F1'
            }}></div>
          </div>
          
          {/* Arrow 2 to 3 */}
          <div style={{
            position: 'absolute',
            top: '30px',
            left: 'calc(50% + 35px)',
            width: 'calc(33.3% - 70px)',
            height: '2px',
            backgroundColor: '#6366F1',
            zIndex: 0
          }}>
            <div style={{
              position: 'absolute',
              right: '-8px',
              top: '-4px',
              width: '0',
              height: '0',
              borderTop: '5px solid transparent',
              borderBottom: '5px solid transparent',
              borderLeft: '8px solid #6366F1'
            }}></div>
          </div>
          
          <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
            <div style={{
              ...circleNumberStyle,
              width: '60px',
              height: '60px',
              marginBottom: '1.5rem',
              backgroundColor: '#EEF2FF',
              color: '#6366F1',
              fontSize: '20px',
              margin: '0 auto'
            }}>1</div>
            <h3 style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: '#1E293B',
              marginBottom: '1rem'
            }}>Describe Your Vision</h3>
            <p style={{
              fontSize: '0.875rem',
              color: '#64748B',
              lineHeight: '1.25rem'
            }}>Provide detailed descriptions of your logo concept and color preferences.</p>
          </div>
          <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
            <div style={{
              ...circleNumberStyle,
              width: '60px',
              height: '60px',
              marginBottom: '1.5rem',
              backgroundColor: '#EEF2FF',
              color: '#6366F1',
              fontSize: '20px',
              margin: '0 auto'
            }}>2</div>
            <h3 style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: '#1E293B',
              marginBottom: '1rem'
            }}>AI Generation</h3>
            <p style={{
              fontSize: '0.875rem',
              color: '#64748B',
              lineHeight: '1.25rem'
            }}>Our AI processes your description and creates unique visual concepts.</p>
          </div>
          <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
            <div style={{
              ...circleNumberStyle,
              width: '60px',
              height: '60px',
              marginBottom: '1.5rem',
              backgroundColor: '#EEF2FF',
              color: '#6366F1',
              fontSize: '20px',
              margin: '0 auto'
            }}>3</div>
            <h3 style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: '#1E293B',
              marginBottom: '1rem'
            }}>Refine & Download</h3>
            <p style={{
              fontSize: '0.875rem',
              color: '#64748B',
              lineHeight: '1.25rem'
            }}>Refine the generated concepts and download your final designs.</p>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button 
            style={{
              backgroundColor: '#4F46E5',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.375rem',
              fontWeight: 600,
              fontSize: '0.875rem',
              border: 'none',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onClick={handleGetStarted}
          >
            Get Started
          </button>
        </div>
      </div>
      
      <div id="create-form">
        <ConceptForm
          onSubmit={handleGenerateConcept}
          status={status}
          error={error}
          onReset={handleReset}
        />
      </div>
      
      {status === 'success' && result && (
        <div className="mt-8 pt-8 border-t border-indigo-100">
          <ConceptResult
            concept={result}
            onRefineRequest={() => {
              // This would navigate to the refinement page with the current concept
              console.log('Navigate to refinement with:', result.generationId);
            }}
            onColorSelect={(color) => handleColorSelect(color)}
            variations={result.variations?.map((variation: {
              name: string;
              colors: string[];
              image_url: string;
              description?: string;
            }) => ({
              name: variation.name,
              colors: variation.colors,
              image_url: variation.image_url,
              description: variation.description
            })) || []}
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

      <div className="mt-20">
        <h2 className="text-2xl font-bold text-indigo-900 mb-10">
          Recent Concepts
        </h2>
        <div style={{...conceptGridStyle, marginTop: '2.5rem'}}>
          {recentConcepts.map((concept) => (
            <div key={concept.id} style={conceptCardStyle}>
              <div style={{ 
                background: `linear-gradient(to right, ${concept.colors[0]}, ${concept.colors[1]})`, 
                height: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <div style={{
                  width: '70px',
                  height: '70px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '20px',
                  color: concept.colors[0]
                }}>
                  {concept.initials}
                </div>
              </div>
              <div style={{padding: '1.25rem 1.5rem', flexGrow: 1}}>
                <h3 style={{
                  fontWeight: 600, 
                  fontSize: '1rem',
                  color: '#1E293B', 
                  marginBottom: '0.5rem'
                }}>
                  {concept.title}
                </h3>
                <p style={{
                  fontSize: '0.875rem',
                  color: '#64748B',
                  lineHeight: '1.25rem',
                  marginBottom: '1rem'
                }}>
                  {concept.description}
                </p>
                <div style={{display: 'flex', gap: '0.5rem', marginBottom: '1.5rem'}}>
                  {concept.colors.map((color, index) => (
                    <span 
                      key={index}
                      style={{ 
                        backgroundColor: color,
                        width: '1.5rem',
                        height: '1.5rem',
                        borderRadius: '9999px',
                        display: 'inline-block'
                      }}
                      title={color}
                    />
                  ))}
                </div>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  paddingTop: '1rem',
                  borderTop: '1px solid #E2E8F0'
                }}>
                  <a 
                    href="#"
                    style={{
                      color: '#6366F1',
                      fontWeight: 500,
                      fontSize: '0.875rem',
                      textDecoration: 'none',
                      cursor: 'pointer',
                      padding: '0.25rem 0'
                    }}
                    onClick={(e) => {
                      e.preventDefault();
                      handleEdit(concept.id);
                    }}
                  >
                    Edit
                  </a>
                  <a 
                    href="#"
                    style={{
                      color: '#6366F1',
                      fontWeight: 500,
                      fontSize: '0.875rem',
                      textDecoration: 'none',
                      cursor: 'pointer',
                      padding: '0.25rem 0'
                    }}
                    onClick={(e) => {
                      e.preventDefault();
                      handleViewDetails(concept.id);
                    }}
                  >
                    View Details
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 