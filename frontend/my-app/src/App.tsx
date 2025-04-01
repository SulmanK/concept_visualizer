import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { ConceptDetail } from './features/ConceptDetail/ConceptDetail';
import { ConceptProvider } from './contexts/ConceptContext';
import { debugSessionStatus, getSessionId, setSessionId } from './services/sessionManager';
import { v4 as uuidv4 } from 'uuid';
import { HomePage } from './features/home/HomePage';
import { ConceptGeneratorPage } from './features/concept-generator';
import { ConceptRefinementPage } from './features/concept-refinement';
import { RecentConceptsPage } from './features/recent-concepts';

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

  // Create a session ID if one doesn't exist
  useEffect(() => {
    const sessionId = getSessionId();
    if (!sessionId) {
      // Generate a unique ID
      const newSessionId = uuidv4();
      console.log('Creating new session ID:', newSessionId);
      setSessionId(newSessionId);
    }
  }, []);

  // Run diagnostic checks on mount
  useEffect(() => {
    const runDiagnostics = async () => {
      // Check session status
      const sessionStatus = debugSessionStatus();
      
      // Check if Supabase connection is working
      let supabaseStatus = 'unknown';
      try {
        const { supabase } = await import('./services/supabaseClient');
        const { data, error } = await supabase.from('concepts').select('count').limit(1);
        
        if (error) {
          supabaseStatus = `Error: ${error.message}`;
          console.error('Supabase connection error:', error);
        } else {
          supabaseStatus = 'Connected';
          console.log('Supabase connection successful:', data);
        }
      } catch (err) {
        supabaseStatus = `Exception: ${err instanceof Error ? err.message : String(err)}`;
        console.error('Exception checking Supabase:', err);
      }
      
      // Store all debug info
      const info = {
        timestamp: new Date().toISOString(),
        sessionStatus,
        supabaseStatus,
        routes: {
          home: window.location.origin + '/',
          recent: window.location.origin + '/recent',
          concepts: window.location.origin + '/concepts/123',
        },
        userAgent: navigator.userAgent,
        screenSize: {
          width: window.innerWidth,
          height: window.innerHeight,
        }
      };
      
      console.log('===== DEBUG INFORMATION =====');
      console.log(JSON.stringify(info, null, 2));
      console.log('=============================');
      
      setDebugInfo(info);
    };
    
    // Wait a moment to run diagnostics to ensure session ID effect completes first
    const timer = setTimeout(runDiagnostics, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div style={appStyle}>
      <ConceptProvider>
        <Router>
          <Routes>
            {/* Main application routes */}
            <Route path="/" element={<MainLayout />}>
              {/* Make HomePage the default homepage */}
              <Route index element={<HomePage />} />
              
              {/* Create concept page */}
              <Route path="create" element={<ConceptGeneratorPage />} />
              
              {/* Refinement routes */}
              <Route path="concepts/refine" element={<ConceptRefinementPage />} />
              
              {/* Concept detail page */}
              <Route path="concepts/:conceptId" element={<ConceptDetail />} />
              
              {/* Recent concepts page */}
              <Route path="recent" element={<RecentConceptsPage />} />
              
              {/* Gallery - shows recent concepts */}
              <Route path="gallery" element={<RecentConceptsPage />} />
              
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