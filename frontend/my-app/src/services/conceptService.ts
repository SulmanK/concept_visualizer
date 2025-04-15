/**
 * Concept API Service
 * 
 * This service provides functions to interact with the concept-related API endpoints
 */

import { API_ENDPOINTS } from '../config/apiEndpoints';
import { apiClient } from './apiClient';
import { ConceptData } from './supabaseClient';  // Reuse existing interfaces

/**
 * Fetch recent concepts from the API
 * 
 * @param userId User ID for which to fetch concepts
 * @param limit Maximum number of concepts to return (default: 10)
 * @returns Promise with array of concept data
 */
export const fetchRecentConceptsFromApi = async (
  userId: string,
  limit: number = 10
): Promise<ConceptData[]> => {
  try {
    const startTime = new Date().getTime();
    console.log(`[API] Fetching recent concepts for user ${userId.substring(0, 6)}... with limit ${limit}`);
    
    const response = await apiClient.get<ConceptData[]>(API_ENDPOINTS.RECENT_CONCEPTS, {
      params: { limit }
    });
    
    const endTime = new Date().getTime();
    console.log(`[API] Fetched ${response.data.length} recent concepts in ${endTime - startTime}ms`);
    
    return response.data;
  } catch (error) {
    console.error('[API] Error fetching recent concepts:', error);
    throw error;
  }
};

/**
 * Fetch concept detail from the API
 * 
 * @param conceptId ID of the concept to fetch
 * @returns Promise with concept data or null if not found
 */
export const fetchConceptDetailFromApi = async (
  conceptId: string
): Promise<ConceptData | null> => {
  try {
    const startTime = new Date().getTime();
    console.log(`[API] Fetching concept detail for ID ${conceptId}`);
    
    const response = await apiClient.get<ConceptData>(API_ENDPOINTS.CONCEPT_DETAIL(conceptId));
    
    const endTime = new Date().getTime();
    console.log(`[API] Fetched concept detail in ${endTime - startTime}ms`);
    
    return response.data;
  } catch (error: any) {
    // Handle 404 - concept not found
    if (error.response && error.response.status === 404) {
      console.log(`[API] Concept with ID ${conceptId} not found`);
      return null;
    }
    
    console.error('[API] Error fetching concept detail:', error);
    throw error;
  }
}; 