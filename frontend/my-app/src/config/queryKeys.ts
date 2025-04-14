/**
 * React Query Key Constants
 * 
 * This file contains centralized constants for all query keys used with React Query.
 * Using these functions instead of hardcoded arrays ensures consistency and makes
 * refactoring and invalidation easier.
 */

export const queryKeys = {
  concepts: {
    all: () => ['concepts'] as const,
    recent: (userId?: string, limit?: number) => 
      [...queryKeys.concepts.all(), 'recent', userId, limit] as const,
    detail: (id?: string, userId?: string) => 
      [...queryKeys.concepts.all(), 'detail', id, userId] as const,
  },
  
  tasks: {
    all: () => ['tasks'] as const,
    detail: (id?: string) => 
      [...queryKeys.tasks.all(), 'detail', id] as const,
  },
  
  mutations: {
    conceptGeneration: () => ['conceptGeneration'] as const,
    conceptRefinement: () => ['conceptRefinement'] as const,
    exportImage: () => ['exportImage'] as const,
  },
  
  rateLimits: () => ['rateLimits'] as const,
  
  user: {
    all: () => ['user'] as const,
    preferences: (userId?: string) => 
      [...queryKeys.user.all(), 'preferences', userId] as const,
  },
}; 