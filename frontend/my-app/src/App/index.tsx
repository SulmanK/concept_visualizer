import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { ConceptGenerator } from '../features/ConceptGenerator';
import { ConceptRefinement } from '../features/ConceptRefinement';
import './App.css';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          {/* Home - Concept Generator */}
          <Route index element={<ConceptGenerator />} />
          
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
  );
} 