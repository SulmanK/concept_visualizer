# Frontend State Management with Supabase Integration

## Overview

This document outlines the state management approach for the Concept Visualizer frontend, including the integration with Supabase for persistent storage of concepts.

## State Management Strategy

The frontend will use a hybrid approach to state management:

1. **React Context** for global application state
2. **Custom hooks** for component-specific state and API integrations
3. **Local Storage** for persisting user preferences
4. **Supabase** for storing and retrieving concepts

## Concept Storage Context

```tsx
// frontend/src/contexts/ConceptContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { ConceptSummary, ConceptDetail } from '../types';
import { useApi } from '../hooks/useApi';

interface ConceptContextType {
  recentConcepts: ConceptSummary[];
  isLoading: boolean;
  error: Error | null;
  refreshRecentConcepts: () => Promise<void>;
  getConceptDetail: (conceptId: string) => Promise<ConceptDetail | null>;
}

const ConceptContext = createContext<ConceptContextType | undefined>(undefined);

export const ConceptProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [recentConcepts, setRecentConcepts] = useState<ConceptSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const api = useApi();

  // Load recent concepts on initial mount
  useEffect(() => {
    refreshRecentConcepts();
  }, []);

  const refreshRecentConcepts = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const concepts = await api.get<ConceptSummary[]>('/api/recent');
      setRecentConcepts(concepts);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load recent concepts'));
      console.error('Error loading recent concepts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getConceptDetail = async (conceptId: string): Promise<ConceptDetail | null> => {
    try {
      return await api.get<ConceptDetail>(`/api/concept/${conceptId}`);
    } catch (err) {
      console.error(`Error loading concept detail for ID ${conceptId}:`, err);
      return null;
    }
  };

  const value = {
    recentConcepts,
    isLoading,
    error,
    refreshRecentConcepts,
    getConceptDetail
  };

  return (
    <ConceptContext.Provider value={value}>
      {children}
    </ConceptContext.Provider>
  );
};

export const useConcepts = (): ConceptContextType => {
  const context = useContext(ConceptContext);
  if (context === undefined) {
    throw new Error('useConcepts must be used within a ConceptProvider');
  }
  return context;
};
```

## API Client with Session Handling

```tsx
// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

class ApiClient {
  private instance: AxiosInstance;
  
  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '',
      headers: {
        'Content-Type': 'application/json',
      },
      // Important: This ensures cookies are sent with requests
      withCredentials: true
    });
    
    // Add response interceptor for error handling
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        // Log errors or perform global error handling
        console.error('API error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }
  
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.get(url, config);
    return response.data;
  }
  
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.post(url, data, config);
    return response.data;
  }
  
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.put(url, data, config);
    return response.data;
  }
  
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.instance.delete(url, config);
    return response.data;
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();
```

## useApi Hook

```tsx
// frontend/src/hooks/useApi.ts
import { useState } from 'react';
import { apiClient } from '../services/api';

export interface ApiState {
  isLoading: boolean;
  error: Error | null;
}

export function useApi() {
  const [state, setState] = useState<ApiState>({
    isLoading: false,
    error: null
  });

  const get = async <T>(url: string): Promise<T> => {
    try {
      setState({ isLoading: true, error: null });
      const result = await apiClient.get<T>(url);
      return result;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown error occurred');
      setState({ isLoading: false, error: err });
      throw err;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const post = async <T>(url: string, data: any): Promise<T> => {
    try {
      setState({ isLoading: true, error: null });
      const result = await apiClient.post<T>(url, data);
      return result;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown error occurred');
      setState({ isLoading: false, error: err });
      throw err;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  return {
    ...state,
    get,
    post,
    put: apiClient.put,
    delete: apiClient.delete
  };
}
```

## Data Models

```tsx
// frontend/src/types/index.ts
export interface ColorPalette {
  name: string;
  colors: string[];  // Hex codes
  description?: string;
  image_url: string;
}

export interface ConceptSummary {
  id: string;
  created_at: string;
  logo_description: string;
  theme_description: string;
  base_image_url: string;
  color_variations: ColorPalette[];
}

export interface ConceptDetail extends ConceptSummary {
  // Additional fields that might be included in the detailed view
}

export interface GenerationResult {
  prompt_id: string;
  image_url: string;
  color_palettes: ColorPalette[];
}

export interface PromptInput {
  logoDescription: string;
  themeDescription: string;
}

export interface RefinementInput {
  originalPromptId: string;
  additionalDetails: string;
}
```

## Updated Concept Generation Hook

```tsx
// frontend/src/hooks/useConceptGeneration.ts
import { useState } from 'react';
import { useApi } from './useApi';
import type { PromptInput, GenerationResult } from '../types';
import { useConcepts } from '../contexts/ConceptContext';

interface ConceptGenerationState {
  isLoading: boolean;
  error: Error | null;
  result: GenerationResult | null;
}

export function useConceptGeneration() {
  const [state, setState] = useState<ConceptGenerationState>({
    isLoading: false,
    error: null,
    result: null
  });
  
  const { refreshRecentConcepts } = useConcepts();
  const api = useApi();
  
  const validateInput = (input: PromptInput): boolean => {
    return (
      !!input.logoDescription.trim() && 
      !!input.themeDescription.trim() &&
      input.logoDescription.length >= 3 &&
      input.themeDescription.length >= 3
    );
  };
  
  const generateConcept = async (input: PromptInput): Promise<void> => {
    if (!validateInput(input)) {
      setState({
        isLoading: false,
        error: new Error('Please provide both logo and theme descriptions (minimum 3 characters each)'),
        result: null
      });
      return;
    }
    
    try {
      setState({ isLoading: true, error: null, result: null });
      
      const result = await api.post<GenerationResult>('/api/generate', {
        logo_description: input.logoDescription,
        theme_description: input.themeDescription
      });
      
      setState({
        isLoading: false,
        error: null,
        result
      });
      
      // Refresh the recent concepts list after successful generation
      await refreshRecentConcepts();
    } catch (error) {
      setState({
        isLoading: false,
        error: error instanceof Error ? error : new Error('Failed to generate concept'),
        result: null
      });
    }
  };
  
  return {
    ...state,
    generateConcept
  };
}
```

## Recent Concepts Component

```tsx
// frontend/src/components/RecentConcepts/RecentConcepts.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useConcepts } from '../../contexts/ConceptContext';
import { Card } from '../Card/Card';
import { ColorPaletteDisplay } from '../ColorPaletteDisplay/ColorPaletteDisplay';
import { LoadingSpinner } from '../LoadingSpinner/LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage/ErrorMessage';
import styles from './RecentConcepts.module.css';

export const RecentConcepts: React.FC = () => {
  const { recentConcepts, isLoading, error, refreshRecentConcepts } = useConcepts();
  
  // Function to get the first two letters of the logo description for the concept display
  const getInitials = (text: string): string => {
    const words = text.trim().split(/\s+/);
    if (words.length === 1) {
      return words[0].substring(0, 2).toUpperCase();
    }
    return (words[0][0] + words[1][0]).toUpperCase();
  };
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (error) {
    return (
      <div className={styles.errorContainer}>
        <ErrorMessage message={error.message} />
        <button 
          className="btn btn-primary mt-4"
          onClick={() => refreshRecentConcepts()}
        >
          Try Again
        </button>
      </div>
    );
  }
  
  if (recentConcepts.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h3 className="text-xl font-medium text-gray-700">No Recent Concepts</h3>
        <p className="text-gray-500 mt-1">
          Your generated concepts will appear here.
        </p>
      </div>
    );
  }
  
  return (
    <div className={styles.container}>
      <h2 className="text-2xl font-bold text-indigo-700 mb-6">Recent Concepts</h2>
      
      <div className={styles.grid}>
        {recentConcepts.map((concept) => (
          <Link to={`/concept/${concept.id}`} key={concept.id}>
            <Card className={styles.conceptCard}>
              <div className={styles.conceptHeader}>
                <div className={styles.conceptInitials}>
                  {getInitials(concept.logo_description)}
                </div>
                <h3 className={styles.conceptTitle}>
                  {concept.logo_description.length > 25 
                    ? `${concept.logo_description.substring(0, 25)}...` 
                    : concept.logo_description}
                </h3>
              </div>
              
              <div className={styles.conceptImage}>
                <img 
                  src={concept.base_image_url} 
                  alt={concept.logo_description} 
                  className={styles.image}
                />
              </div>
              
              <div className={styles.conceptPalettes}>
                {concept.color_variations.slice(0, 1).map((palette, index) => (
                  <div key={index} className={styles.paletteContainer}>
                    <h4 className={styles.paletteName}>{palette.name}</h4>
                    <ColorPaletteDisplay colors={palette.colors} size="small" />
                  </div>
                ))}
                {concept.color_variations.length > 1 && (
                  <div className={styles.moreIndicator}>
                    +{concept.color_variations.length - 1} more
                  </div>
                )}
              </div>
              
              <div className={styles.conceptMeta}>
                <span className={styles.dateLabel}>
                  {new Date(concept.created_at).toLocaleDateString()}
                </span>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
};
```

## Application Setup

To properly integrate this state management approach, the following setup is required:

```tsx
// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConceptProvider } from './contexts/ConceptContext';
import { Header } from './components/Header/Header';
import { Footer } from './components/Footer/Footer';
import { Home } from './pages/Home/Home';
import { ConceptGenerator } from './pages/ConceptGenerator/ConceptGenerator';
import { ConceptRefinement } from './pages/ConceptRefinement/ConceptRefinement';
import { ConceptDetail } from './pages/ConceptDetail/ConceptDetail';
import './App.css';

function App() {
  return (
    <Router>
      <ConceptProvider>
        <div className="app-container">
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/create" element={<ConceptGenerator />} />
              <Route path="/refine/:promptId" element={<ConceptRefinement />} />
              <Route path="/concept/:conceptId" element={<ConceptDetail />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </ConceptProvider>
    </Router>
  );
}

export default App;
```

## CSS Modules for Recent Concepts

```css
/* frontend/src/components/RecentConcepts/RecentConcepts.module.css */
.container {
  width: 100%;
  padding: 1rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.conceptCard {
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.conceptCard:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.1), 0 10px 10px -5px rgba(67, 56, 202, 0.04);
}

.conceptHeader {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.conceptInitials {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #fff;
  color: #4338CA;
  font-weight: 600;
  margin-right: 0.75rem;
  box-shadow: 0 0 0 2px rgba(67, 56, 202, 0.2);
}

.conceptTitle {
  font-size: 1rem;
  font-weight: 500;
  color: #1F2937;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conceptImage {
  width: 100%;
  height: 180px;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1rem;
}

.image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.conceptPalettes {
  margin-bottom: 1rem;
}

.paletteContainer {
  margin-bottom: 0.5rem;
}

.paletteName {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4B5563;
  margin-bottom: 0.25rem;
}

.moreIndicator {
  font-size: 0.75rem;
  color: #6B7280;
  text-align: right;
  margin-top: 0.25rem;
}

.conceptMeta {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid #E5E7EB;
  display: flex;
  justify-content: flex-end;
}

.dateLabel {
  font-size: 0.75rem;
  color: #6B7280;
}

.errorContainer {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  text-align: center;
}

.emptyState {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background-color: rgba(249, 250, 251, 0.8);
  border-radius: 0.5rem;
}
```

## Concept Detail Page

```tsx
// frontend/src/pages/ConceptDetail/ConceptDetail.tsx
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useConcepts } from '../../contexts/ConceptContext';
import { LoadingSpinner } from '../../components/LoadingSpinner/LoadingSpinner';
import { ErrorMessage } from '../../components/ErrorMessage/ErrorMessage';
import { Card } from '../../components/Card/Card';
import { ColorPaletteDisplay } from '../../components/ColorPaletteDisplay/ColorPaletteDisplay';
import type { ConceptDetail as ConceptDetailType } from '../../types';
import styles from './ConceptDetail.module.css';

export const ConceptDetail: React.FC = () => {
  const { conceptId } = useParams<{ conceptId: string }>();
  const { getConceptDetail } = useConcepts();
  const [concept, setConcept] = useState<ConceptDetailType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    async function loadConceptDetail() {
      if (!conceptId) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        const conceptDetail = await getConceptDetail(conceptId);
        if (conceptDetail) {
          setConcept(conceptDetail);
        } else {
          setError(new Error('Concept not found'));
        }
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load concept'));
      } finally {
        setIsLoading(false);
      }
    }
    
    loadConceptDetail();
  }, [conceptId, getConceptDetail]);
  
  if (isLoading) {
    return <LoadingSpinner size="large" />;
  }
  
  if (error || !concept) {
    return (
      <div className={styles.errorContainer}>
        <ErrorMessage message={error?.message || 'Concept not found'} />
        <Link to="/" className="btn btn-primary mt-4">
          Back to Home
        </Link>
      </div>
    );
  }
  
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>{concept.logo_description}</h1>
        <p className={styles.subtitle}>{concept.theme_description}</p>
        <div className={styles.meta}>
          <span className={styles.date}>
            Created on {new Date(concept.created_at).toLocaleDateString()}
          </span>
        </div>
      </header>
      
      <div className={styles.content}>
        <section className={styles.mainImage}>
          <img 
            src={concept.base_image_url} 
            alt={concept.logo_description} 
            className={styles.image}
          />
        </section>
        
        <section className={styles.palettes}>
          <h2 className={styles.sectionTitle}>Color Palettes</h2>
          <div className={styles.palettesGrid}>
            {concept.color_variations.map((palette, index) => (
              <Card key={index} className={styles.paletteCard}>
                <h3 className={styles.paletteName}>{palette.name}</h3>
                {palette.description && (
                  <p className={styles.paletteDescription}>{palette.description}</p>
                )}
                <div className={styles.paletteImage}>
                  <img 
                    src={palette.image_url} 
                    alt={`${concept.logo_description} with ${palette.name} colors`} 
                    className={styles.image}
                  />
                </div>
                <ColorPaletteDisplay 
                  colors={palette.colors} 
                  size="large" 
                  showHexCodes 
                />
              </Card>
            ))}
          </div>
        </section>
        
        <section className={styles.actions}>
          <Link 
            to={`/refine/${concept.id}`} 
            className="btn btn-primary"
          >
            Refine This Concept
          </Link>
          <Link 
            to="/create" 
            className="btn btn-outline"
          >
            Create New Concept
          </Link>
        </section>
      </div>
    </div>
  );
};
```

## Environment Configuration

The frontend will need the following environment variables:

```
# .env
VITE_API_BASE_URL=http://localhost:8000
```

By implementing this state management approach, the frontend will be able to:

1. Store and retrieve concepts via the backend's Supabase integration
2. Maintain session state across browser sessions via HTTP-only cookies
3. Display recent concepts to users based on their session
4. Provide a consistent experience across the application 