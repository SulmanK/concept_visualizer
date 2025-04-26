import { vi, describe, it, expect, beforeEach } from "vitest";
import {
  fetchRecentConceptsFromApi,
  fetchConceptDetailFromApi,
} from "../conceptService";
import { apiClient } from "../apiClient";
import { API_ENDPOINTS } from "../../config/apiEndpoints";
import { AxiosError } from "axios";

// Mock dependencies
vi.mock("../apiClient", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

vi.mock("../../config/apiEndpoints", () => ({
  API_ENDPOINTS: {
    RECENT_CONCEPTS: "/concepts/list",
    CONCEPT_DETAIL: (id: string) => `/concepts/${id}`,
  },
}));

// Sample concept data for testing
const mockConceptData = {
  id: "test-concept-id",
  user_id: "test-user-id",
  logo_description: "A modern tech startup logo",
  theme_description: "Minimalist corporate design with blue tones",
  image_path: "images/test-concept.png",
  image_url: "https://example.com/images/test-concept.png",
  created_at: "2023-01-01T00:00:00Z",
  color_variations: [
    {
      id: "variation-1",
      concept_id: "test-concept-id",
      palette_name: "Cool Blue",
      colors: ["#1a2b3c", "#4d5e6f", "#789abc"],
      image_path: "images/variation-1.png",
      image_url: "https://example.com/images/variation-1.png",
      created_at: "2023-01-01T00:00:00Z",
    },
  ],
};

describe("Concept Service", () => {
  // Create console spy to prevent noisy output
  const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
  const consoleErrorSpy = vi
    .spyOn(console, "error")
    .mockImplementation(() => {});

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("fetchRecentConceptsFromApi", () => {
    it("should call the API with correct parameters", async () => {
      // Mock API response
      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: [mockConceptData],
      });

      // Call the function
      const result = await fetchRecentConceptsFromApi("test-user-id", 5);

      // Verify API was called correctly
      expect(apiClient.get).toHaveBeenCalledWith(
        API_ENDPOINTS.RECENT_CONCEPTS,
        { params: { limit: 5 } },
      );

      // Verify result
      expect(result).toEqual([mockConceptData]);

      // Verify logs
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("Fetching recent concepts for user"),
      );
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("Fetched 1 recent concepts"),
      );
    });

    it("should use default limit if not provided", async () => {
      // Mock API response
      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: [mockConceptData],
      });

      // Call the function without limit
      await fetchRecentConceptsFromApi("test-user-id");

      // Verify default limit (10) was used
      expect(apiClient.get).toHaveBeenCalledWith(
        API_ENDPOINTS.RECENT_CONCEPTS,
        { params: { limit: 10 } },
      );
    });

    it("should handle API errors", async () => {
      // Mock API error
      const mockError = new Error("API error");
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      // Call the function and expect it to throw
      await expect(fetchRecentConceptsFromApi("test-user-id")).rejects.toThrow(
        "API error",
      );

      // Verify error was logged
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Error fetching recent concepts"),
        mockError,
      );
    });

    it("should log detailed information about color variations", async () => {
      // Mock API response with multiple concepts having variations
      const mockConcepts = [
        {
          ...mockConceptData,
          id: "concept-1",
          color_variations: [
            { id: "var-1", colors: ["#123"], image_url: "url1" },
            { id: "var-2", colors: ["#456"], image_url: "url2" },
            { id: "var-3", colors: ["#789"], image_url: "url3" },
          ],
        },
        {
          ...mockConceptData,
          id: "concept-2",
          color_variations: [],
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: mockConcepts,
      });

      // Call the function
      await fetchRecentConceptsFromApi("test-user-id");

      // Verify logs about variations
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "Concept 1/2 (ID: concept-1): 3 color variations",
        ),
      );
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "Concept 2/2 (ID: concept-2): 0 color variations",
        ),
      );
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("... and 1 more variations"),
      );
    });
  });

  describe("fetchConceptDetailFromApi", () => {
    it("should call the API with correct concept ID", async () => {
      // Mock API response
      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: mockConceptData,
      });

      // Call the function
      const result = await fetchConceptDetailFromApi("test-concept-id");

      // Verify API was called correctly
      expect(apiClient.get).toHaveBeenCalledWith(
        API_ENDPOINTS.CONCEPT_DETAIL("test-concept-id"),
      );

      // Verify result
      expect(result).toEqual(mockConceptData);

      // Verify logs
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "Fetching concept detail for ID test-concept-id",
        ),
      );
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("Fetched concept detail"),
      );
    });

    it("should return null for 404 errors", async () => {
      // Create a custom error object that will pass the instanceof AxiosError check
      const error = {
        isAxiosError: true,
        response: {
          status: 404,
          statusText: "Not Found",
        },
        message: "Request failed with status code 404",
        name: "AxiosError",
        toJSON: () => ({ message: "Request failed with status code 404" }),
      };

      // Make the error pass instanceof AxiosError check
      Object.setPrototypeOf(error, AxiosError.prototype);

      vi.mocked(apiClient.get).mockRejectedValueOnce(error);

      // Call the function
      const result = await fetchConceptDetailFromApi("nonexistent-id");

      // Verify result is null (not throwing)
      expect(result).toBeNull();

      // Verify logs
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("Concept with ID nonexistent-id not found"),
      );
    });

    it("should throw for non-404 errors", async () => {
      // Mock API error
      const mockError = new Error("Server error");
      (mockError as unknown as { response: { status: number } }).response = {
        status: 500,
      };
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      // Call the function and expect it to throw
      await expect(
        fetchConceptDetailFromApi("test-concept-id"),
      ).rejects.toThrow("Server error");

      // Verify error was logged
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Error fetching concept detail"),
        mockError,
      );
    });
  });
});
