/**
 * Concept API Service
 *
 * This service provides functions to interact with the concept-related API endpoints
 */

import { API_ENDPOINTS } from "../config/apiEndpoints";
import { apiClient } from "./apiClient";
import { ConceptData } from "./supabaseClient"; // Reuse existing interfaces
import { AxiosError } from "axios";

/**
 * Fetch recent concepts from the API
 *
 * @param userId User ID for which to fetch concepts
 * @param limit Maximum number of concepts to return (default: 10)
 * @returns Promise with array of concept data
 */
export const fetchRecentConceptsFromApi = async (
  userId: string,
  limit: number = 10,
): Promise<ConceptData[]> => {
  try {
    const startTime = new Date().getTime();
    console.log(
      `[API] Fetching recent concepts for user ${userId.substring(
        0,
        6,
      )}... with limit ${limit}`,
    );

    const response = await apiClient.get<ConceptData[]>(
      API_ENDPOINTS.RECENT_CONCEPTS,
      {
        params: { limit },
      },
    );

    const endTime = new Date().getTime();
    console.log(
      `[API] Fetched ${response.data.length} recent concepts in ${
        endTime - startTime
      }ms`,
    );

    // Add detailed logging for color variations
    response.data.forEach((concept, index) => {
      const variationsCount = concept.color_variations?.length || 0;
      console.log(
        `[API] Concept ${index + 1}/${response.data.length} (ID: ${
          concept.id
        }): ${variationsCount} color variations`,
      );

      // If variations exist, log details of first few
      if (variationsCount > 0 && concept.color_variations) {
        concept.color_variations.slice(0, 2).forEach((variation, i) => {
          console.log(
            `[API] - Variation ${i + 1}: ID ${variation.id}, Colors: ${
              variation.colors.length
            }, Image URL exists: ${!!variation.image_url}`,
          );
        });
        if (variationsCount > 2) {
          console.log(`[API] - ... and ${variationsCount - 2} more variations`);
        }
      }
    });

    return response.data;
  } catch (error) {
    console.error("[API] Error fetching recent concepts:", error);
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
  conceptId: string,
): Promise<ConceptData | null> => {
  try {
    const startTime = new Date().getTime();
    console.log(`[API] Fetching concept detail for ID ${conceptId}`);

    const response = await apiClient.get<ConceptData>(
      API_ENDPOINTS.CONCEPT_DETAIL(conceptId),
    );

    const endTime = new Date().getTime();
    console.log(`[API] Fetched concept detail in ${endTime - startTime}ms`);

    return response.data;
  } catch (error: unknown) {
    // Handle 404 - concept not found
    if (error instanceof AxiosError && error.response?.status === 404) {
      console.log(`[API] Concept with ID ${conceptId} not found`);
      return null;
    }

    console.error("[API] Error fetching concept detail:", error);
    throw error;
  }
};
