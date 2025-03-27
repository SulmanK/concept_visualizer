import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { ConceptGenerator } from './features/ConceptGenerator';
import { ConceptRefinement } from './features/ConceptRefinement';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          {/* Home - Concept Generator */}
          <Route index element={<ConceptGenerator />} />
          
          {/* Refinement routes */}
          <Route path="refine" element={<ConceptRefinement />} />
          <Route path="refine/:conceptId" element={<ConceptRefinement />} />
          
          {/* Gallery - not implemented in this phase */}
          <Route path="gallery" element={<div className="text-center py-16">
            <h1 className="text-2xl font-bold text-dark-900 mb-2">Concept Gallery</h1>
            <p className="text-dark-600">Coming soon in the next phase!</p>
          </div>} />
          
          {/* Fallback for unknown routes */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
