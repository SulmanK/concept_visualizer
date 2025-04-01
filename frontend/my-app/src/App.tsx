import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { ConceptProvider } from './contexts/ConceptContext';
import { debugSessionStatus, getSessionId, ensureSession } from './services/sessionManager';
import { LandingPage } from './features/landing';
import { ConceptDetailPage } from './features/concepts/detail';
import { RecentConceptsPage } from './features/concepts/recent';
import { CreateConceptPage } from './features/concepts/create';
import { RefinementPage, RefinementSelectionPage } from './features/refinement';

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

export default function App() {
  const [debugInfo, setDebugInfo] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize session on app load
  useEffect(() => {
    const initializeSession = async () => {
      try {
        // Ensure a session exists - this will generate a UUID if needed
        // and sync with the backend
        const isNewSession = await ensureSession();
        console.log(`Session initialization completed. New session created: ${isNewSession}`);
        
        // Get the session status for debugging
        const sessionStatus = debugSessionStatus();
        
        // Log general app information
        console.log('===== DEBUG INFORMATION =====');
        console.log({
          timestamp: new Date().toISOString(),
          sessionStatus,
          sessionId: getSessionId(),
          isNewSession,
          supabaseStatus: 'Connected', // We assume it's connected at this point
          routes: {
            home: 'http://localhost:5173/',
            recent: 'http://localhost:5173/recent',
            concepts: 'http://localhost:5173/concepts/123' // Example
          },
          userAgent: navigator.userAgent,
          screenSize: {
            width: window.innerWidth,
            height: window.innerHeight
          }
        });
        console.log('=============================');
        
        setDebugInfo({
          sessionStatus,
          supabaseStatus: 'Connected',
        });
        
        setIsInitialized(true);
      } catch (error) {
        console.error('Error initializing session:', error);
        setIsInitialized(true); // Still mark as initialized to not block UI
      }
    };
    
    initializeSession();
  }, []);

  return (
    <div style={appStyle}>
      <ConceptProvider>
        <Router>
          <Routes>
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
        </Router>
      </ConceptProvider>
      
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
          Session: {debugInfo.sessionStatus?.exists ? '✅' : '❌'} | 
          Supabase: {debugInfo.supabaseStatus === 'Connected' ? '✅' : '❌'}
        </div>
      )}
    </div>
  );
} 