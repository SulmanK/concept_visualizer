import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { ConceptGenerator } from '../features/ConceptGenerator';
import { ConceptRefinement } from '../features/ConceptRefinement';
import './App.css';

// Ensure no gaps and full width but allow MainLayout to control its content width
const appStyle = {
  margin: 0,
  padding: 0,
  width: '100%',
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column' as const,
  position: 'relative' as const,
  overflow: 'hidden'
};

export default function App() {
  return (
    <div style={appStyle}>
      <Router>
        <Routes>
          {/* Main application routes */}
          <Route path="/" element={<MainLayout />}>
            {/* Make ConceptGenerator the default homepage */}
            <Route index element={<ConceptGenerator />} />
            
            {/* Create concept page - same as homepage for consistent navigation */}
            <Route path="create" element={<ConceptGenerator />} />
            
            {/* Refinement routes */}
            <Route path="refine" element={<div>Please select a concept to refine</div>} />
            <Route path="refine/:conceptId" element={<ConceptRefinement />} />
            
            {/* Gallery - not implemented in this phase */}
            <Route path="gallery" element={<div>Gallery - Coming Soon</div>} />
            
            {/* Fallback for unknown routes */}
            <Route path="*" element={<div>Page not found</div>} />
          </Route>
        </Routes>
      </Router>
    </div>
  );
} 