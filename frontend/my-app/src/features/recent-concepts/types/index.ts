/**
 * Types specific to the Recent Concepts feature
 */
import { StoredConcept, ColorVariation } from '../../../types/concept.types';

/**
 * Props for ConceptCard component
 */
export interface ConceptCardProps {
  concept: StoredConcept;
}

/**
 * Context state for recent concepts
 */
export interface RecentConceptsState {
  recentConcepts: StoredConcept[];
  loadingConcepts: boolean;
  errorLoadingConcepts: string | null;
  refreshConcepts: () => void;
} 