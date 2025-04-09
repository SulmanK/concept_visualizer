import { useState, useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import MainLayout from './components/layout/MainLayout';
import PageTransition from './components/layout/PageTransition';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './hooks/useToast';
import { RateLimitProvider } from './contexts/RateLimitContext';
import { ErrorBoundary, OfflineStatus } from './components/ui';
import ApiToastListener from './components/ui/ApiToastListener';

// Lazy load pages instead of importing them directly
const LandingPage = lazy(() => import('./features/landing').then(module => ({ default: module.LandingPage })));
const ConceptDetailPage = lazy(() => import('./features/concepts/detail').then(module => ({ default: module.ConceptDetailPage })));
const RecentConceptsPage = lazy(() => import('./features/concepts/recent').then(module => ({ default: module.RecentConceptsPage })));
const CreateConceptPage = lazy(() => import('./features/concepts/create').then(module => ({ default: module.CreateConceptPage })));
const RefinementPage = lazy(() => import('./features/refinement').then(module => ({ default: module.RefinementPage })));
const RefinementSelectionPage = lazy(() => import('./features/refinement').then(module => ({ default: module.RefinementSelectionPage })));

// Loading fallback component
const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh',
    background: 'linear-gradient(135deg, #f5f7ff 0%, #c3cfe2 100%)'
  }}>
    <div style={{ 
      padding: '20px', 
      borderRadius: '8px', 
      backgroundColor: 'white',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      <p className="mt-4 text-indigo-600 font-medium">Loading...</p>
    </div>
  </div>
);

// Import animations CSS
import './styles/animations.css';

// Ensure no gaps and full width but allow MainLayout to control its content width
const appStyle = {
  margin: 0,
  padding: 0,
  width: '100%',
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column' as const,
  position: 'relative' as const,
  overflow: 'hidden',
  background: 'linear-gradient(135deg, #f5f7ff 0%, #c3cfe2 100%)',
  fontFamily: '"Inter", sans-serif',
};

/**
 * Routes component to handle the route transitions
 */
const AppRoutes = () => {
  const location = useLocation();
  
  // Determine the appropriate transition type based on pathname
  const getTransitionType = (pathname: string) => {
    // Using a slide-up transition for concept detail pages
    if (pathname.includes('/concepts/')) {
      return 'slide-up';
    }
    
    // Using slide-left for refinement pages
    if (pathname.includes('/refine')) {
      return 'slide-left';
    }
    
    // Default fade transition for other routes
    return 'fade';
  };
  
  return (
    // Temporarily bypassing PageTransition to diagnose state sync issues
    // <PageTransition transitionType={getTransitionType(location.pathname)}>
      <Suspense fallback={<LoadingFallback />}>
        <Routes location={location}>
          {/* Main application routes */}
          <Route path="/" element={<MainLayout />}>
            {/* Make LandingPage the default homepage */}
            <Route index element={<LandingPage />} />
            
            {/* Create page */}
            <Route path="create" element={<CreateConceptPage />} />
            
            {/* Concept detail page */}
            <Route path="concepts/:conceptId" element={<ConceptDetailPage />} />
            
            {/* Recent concepts page */}
            <Route path="recent" element={<RecentConceptsPage />} />
            
            {/* Refinement selection page */}
            <Route path="refine" element={<RefinementSelectionPage />} />
            
            {/* Refinement page with concept ID */}
            <Route path="refine/:conceptId" element={<RefinementPage />} />
            
            {/* Fallback for unknown routes */}
            <Route path="*" element={<div>Page not found</div>} />
          </Route>
        </Routes>
      </Suspense>
    // </PageTransition>
  );
};

// Set up a global fetch interceptor for rate limit headers
import { extractRateLimitHeaders } from './services/rateLimitService';

// Create a function to set up the global fetch interceptor
const setupFetchInterceptor = () => {
  const originalFetch = window.fetch;
  
  window.fetch = async function(input, init) {
    // Call the original fetch
    const response = await originalFetch.call(window, input, init);
    
    // Only process API requests (check both string URLs and Request objects)
    if ((typeof input === 'string' && input.includes('/api/')) || 
        (input instanceof Request && input.url.includes('/api/'))) {
      try {
        // Clone the response to avoid consuming the body
        const responseClone = response.clone();
        
        // Extract the URL from either string or Request object
        const url = typeof input === 'string' ? input : input.url;
        
        // Extract and process rate limit headers
        if (!url.includes('/health/rate-limits')) {
          extractRateLimitHeaders(responseClone, url);
        }
      } catch (error) {
        console.error('Error in fetch interceptor:', error);
      }
    }
    
    return response;
  };
};

export default function App() {
  const [debugInfo, setDebugInfo] = useState<any>(null);

  // Set up the fetch interceptor only once on app initialization
  useEffect(() => {
    setupFetchInterceptor();
    console.log('Global fetch interceptor for rate limits has been set up');
  }, []);

  // Set basic debug info for development environment
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      setDebugInfo({
        environment: process.env.NODE_ENV,
        apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
        supabaseUrl: import.meta.env.VITE_SUPABASE_URL || 'Not configured',
      });
    }
  }, []);

  return (
    <div style={appStyle}>
      <ToastProvider position="bottom-right" defaultDuration={5000} maxToasts={5}>
        <ErrorBoundary errorMessage="Something went wrong in the application. Please try refreshing the page.">
          <ApiToastListener />
          <AuthProvider>
            <RateLimitProvider>
              <Router>
                {/* Offline status notification */}
                <OfflineStatus 
                  position="top"
                  showConnectionInfo={true}
                />
                
                <AppRoutes />
              </Router>
            </RateLimitProvider>
          </AuthProvider>
        </ErrorBoundary>
      </ToastProvider>
      
      {/* Debugging overlay - only shown in development */}
      {process.env.NODE_ENV === 'development' && debugInfo && (
        <div 
          style={{
            position: 'fixed',
            bottom: '10px',
            right: '10px',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '5px 10px',
            borderRadius: '5px',
            fontSize: '12px',
            zIndex: 9999,
            cursor: 'pointer'
          }}
          onClick={() => console.log('Debug info:', debugInfo)}
        >
          ENV: {debugInfo.environment} | 
          API: {debugInfo.apiBaseUrl ? '✅' : '❌'}
        </div>
      )}
      
      {/* Add React Query DevTools for better debugging */}
      <ReactQueryDevtools initialIsOpen={false} position="left" />
    </div>
  );
} 