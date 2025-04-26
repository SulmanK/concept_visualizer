/**
 * Mock API service for testing purposes.
 * This service simulates responses from the backend API without making actual network calls.
 */

import {
  ApiResponse,
  ApiError,
  GenerationResponse,
  PromptRequest,
  RefinementRequest,
} from "../../types";

/**
 * Default mock responses for various API endpoints
 */
const mockResponses = {
  generateConcept: {
    success: {
      imageUrl: "https://example.com/mock-concept.png",
      colorPalette: {
        primary: "#4F46E5",
        secondary: "#818CF8",
        accent: "#C4B5FD",
        background: "#F5F3FF",
        text: "#1E1B4B",
      },
      generationId: "mock-gen-123",
      createdAt: new Date().toISOString(),
    },
    error: {
      status: 500,
      message: "Failed to generate concept",
    },
  },
  refineConcept: {
    success: {
      imageUrl: "https://example.com/mock-refined-concept.png",
      colorPalette: {
        primary: "#6366F1",
        secondary: "#A5B4FC",
        accent: "#E0E7FF",
        background: "#EEF2FF",
        text: "#312E81",
      },
      generationId: "mock-refine-123",
      createdAt: new Date().toISOString(),
      originalImageUrl: "https://example.com/mock-concept.png",
      refinementPrompt: "Make it more vibrant",
    },
    error: {
      status: 500,
      message: "Failed to refine concept",
    },
  },
};

/**
 * Configuration options for the mock API service
 */
export interface MockApiConfig {
  shouldFail?: boolean;
  responseDelay?: number;
  customResponses?: {
    generateConcept?: Partial<GenerationResponse>;
    refineConcept?: Partial<GenerationResponse>;
  };
}

/**
 * Default configuration
 */
const defaultConfig: MockApiConfig = {
  shouldFail: false,
  responseDelay: 500,
};

/**
 * Mock API service that simulates the concept visualizer backend
 */
export class MockApiService {
  private config: MockApiConfig;

  constructor(config: MockApiConfig = defaultConfig) {
    this.config = { ...defaultConfig, ...config };
  }

  /**
   * Simulates a delayed response
   */
  private async delay(): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(resolve, this.config.responseDelay),
    );
  }

  /**
   * Simulates a response with the specified data or error
   */
  private async simulateResponse<T>(
    successData: T,
    errorData: ApiError,
  ): Promise<ApiResponse<T>> {
    await this.delay();

    if (this.config.shouldFail) {
      return { error: errorData, loading: false };
    }

    return { data: successData, loading: false };
  }

  /**
   * Simulates the concept generation endpoint
   */
  async generateConcept(
    request: PromptRequest,
  ): Promise<ApiResponse<GenerationResponse>> {
    // Validate inputs (similar to real implementation)
    if (!request.logoDescription || !request.themeDescription) {
      return {
        error: {
          status: 400,
          message: "Logo and theme descriptions are required",
        },
        loading: false,
      };
    }

    // Use custom response if provided or fallback to default mock
    const successResponse = {
      ...mockResponses.generateConcept.success,
      ...this.config.customResponses?.generateConcept,
    };

    return this.simulateResponse<GenerationResponse>(
      successResponse,
      mockResponses.generateConcept.error,
    );
  }

  /**
   * Simulates the concept refinement endpoint
   */
  async refineConcept(
    request: RefinementRequest,
  ): Promise<ApiResponse<GenerationResponse>> {
    // Validate inputs (similar to real implementation)
    if (!request.originalImageUrl || !request.refinementPrompt) {
      return {
        error: {
          status: 400,
          message: "Original image URL and refinement prompt are required",
        },
        loading: false,
      };
    }

    // Use custom response if provided or fallback to default mock
    const successResponse = {
      ...mockResponses.refineConcept.success,
      ...this.config.customResponses?.refineConcept,
      originalImageUrl: request.originalImageUrl,
      refinementPrompt: request.refinementPrompt,
    };

    return this.simulateResponse<GenerationResponse>(
      successResponse,
      mockResponses.refineConcept.error,
    );
  }

  /**
   * Configure the mock API service
   */
  configure(config: Partial<MockApiConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

/**
 * Singleton instance of the mock API service
 */
export const mockApiService = new MockApiService();

/**
 * Creates a wrapped API response matching the useApi hook's return value
 */
export function createMockApiResponse<T>(
  data?: T,
  error?: ApiError,
): ApiResponse<T> {
  return {
    data,
    error,
    loading: false,
  };
}
