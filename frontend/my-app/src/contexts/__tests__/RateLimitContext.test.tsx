import React from "react";
import {
  render,
  screen,
  waitFor,
  act,
  renderHook,
} from "@testing-library/react";
import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mocked state for the tests
let mockRateLimitsData = {
  user_identifier: "test-user",
  limits: {
    generate_concept: { limit: "10/day", remaining: 8, reset_after: 86400 },
    refine_concept: { limit: "5/day", remaining: 4, reset_after: 86400 },
    store_concept: { limit: "25/day", remaining: 22, reset_after: 86400 },
    get_concepts: { limit: "100/day", remaining: 98, reset_after: 86400 },
    sessions: { limit: "10/hour", remaining: 9, reset_after: 3600 },
    export_action: { limit: "10/day", remaining: 9, reset_after: 86400 },
  },
  default_limits: ["generate_concept", "refine_concept"],
};
let mockIsLoading = false;
let mockError = null;

// Mock the useRateLimitsQuery hook
const decrementLimitMock = vi.fn((category, amount = 1) => {
  // Mock implementation to update the mockRateLimitsData
  if (
    mockRateLimitsData &&
    mockRateLimitsData.limits &&
    mockRateLimitsData.limits[category]
  ) {
    mockRateLimitsData.limits[category].remaining = Math.max(
      0,
      mockRateLimitsData.limits[category].remaining - amount,
    );
  }
});

const refetchMock = vi.fn(async () => ({
  data: mockRateLimitsData,
  error: null,
  isSuccess: true,
}));

// Mock both hooks from useRateLimitsQuery module
vi.mock("../../hooks/useRateLimitsQuery", () => {
  return {
    useRateLimitsQuery: () => ({
      data: mockRateLimitsData,
      isLoading: mockIsLoading,
      error: mockError,
      refetch: refetchMock,
      decrementLimit: decrementLimitMock,
    }),
    useOptimisticRateLimitUpdate: () => ({
      decrementLimit: decrementLimitMock,
    }),
  };
});

// Import after the mock is set up
import {
  RateLimitProvider,
  useRateLimitContext,
  useRateLimitsData,
  useRateLimitsLoading,
  useRateLimitsError,
  useRateLimitsRefetch,
  useRateLimitsDecrement,
} from "../RateLimitContext";
import * as useRateLimitsQueryModule from "../../hooks/useRateLimitsQuery";

// Component that consumes the context for testing
const TestRateLimitConsumer = () => {
  const { rateLimits, isLoading, error, refetch, decrementLimit } =
    useRateLimitContext();

  return (
    <div>
      <div data-testid="loading">{String(isLoading)}</div>
      <div data-testid="error">{error || "no-error"}</div>
      <div data-testid="limits">
        {rateLimits
          ? JSON.stringify(rateLimits.limits.generate_concept)
          : "no-data"}
      </div>
      <button data-testid="refetch" onClick={() => refetch(true)}>
        Refetch
      </button>
      <button
        data-testid="decrement"
        onClick={() => decrementLimit("generate_concept", 1)}
      >
        Decrement
      </button>
    </div>
  );
};

// Create wrapper function for the tests
const createWrapper = (queryClient: QueryClient) => {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <RateLimitProvider>{children}</RateLimitProvider>
      </QueryClientProvider>
    );
  };
};

describe("RateLimitContext", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    // Reset mocked state
    mockRateLimitsData = {
      user_identifier: "test-user",
      limits: {
        generate_concept: { limit: "10/day", remaining: 8, reset_after: 86400 },
        refine_concept: { limit: "5/day", remaining: 4, reset_after: 86400 },
        store_concept: { limit: "25/day", remaining: 22, reset_after: 86400 },
        get_concepts: { limit: "100/day", remaining: 98, reset_after: 86400 },
        sessions: { limit: "10/hour", remaining: 9, reset_after: 3600 },
        export_action: { limit: "10/day", remaining: 9, reset_after: 86400 },
      },
      default_limits: ["generate_concept", "refine_concept"],
    };
    mockIsLoading = false;
    mockError = null;

    // Clear mocks
    vi.clearAllMocks();

    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  describe("RateLimitProvider", () => {
    it("should provide rate limits data to consumers", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <RateLimitProvider>
            <TestRateLimitConsumer />
          </RateLimitProvider>
        </QueryClientProvider>,
      );

      // Data should be passed to the consumer
      const limitData = JSON.parse(
        screen.getByTestId("limits").textContent as string,
      );
      expect(limitData).toEqual(mockRateLimitsData.limits.generate_concept);
    });

    it("should pass loading state to consumers", () => {
      // Update mock to show loading
      mockIsLoading = true;

      render(
        <QueryClientProvider client={queryClient}>
          <RateLimitProvider>
            <TestRateLimitConsumer />
          </RateLimitProvider>
        </QueryClientProvider>,
      );

      // Loading state should be passed to the consumer
      expect(screen.getByTestId("loading").textContent).toBe("true");
    });

    it("should pass error state to consumers", () => {
      // Update mock to include an error
      mockError = new Error("Failed to fetch rate limits");

      render(
        <QueryClientProvider client={queryClient}>
          <RateLimitProvider>
            <TestRateLimitConsumer />
          </RateLimitProvider>
        </QueryClientProvider>,
      );

      // Error should be passed to the consumer
      expect(screen.getByTestId("error").textContent).toBe(
        "Failed to fetch rate limits",
      );
    });
  });

  describe("Context actions", () => {
    it("should call refetch with force=true when refetch is called", async () => {
      render(
        <QueryClientProvider client={queryClient}>
          <RateLimitProvider>
            <TestRateLimitConsumer />
          </RateLimitProvider>
        </QueryClientProvider>,
      );

      // Click refetch button
      screen.getByTestId("refetch").click();

      // Should have called refetch
      expect(refetchMock).toHaveBeenCalled();
    });

    it("should call decrementLimit when decrementLimit is called", async () => {
      render(
        <QueryClientProvider client={queryClient}>
          <RateLimitProvider>
            <TestRateLimitConsumer />
          </RateLimitProvider>
        </QueryClientProvider>,
      );

      // Click decrement button
      screen.getByTestId("decrement").click();

      // Should have called decrementLimit with the right parameters
      expect(decrementLimitMock).toHaveBeenCalledWith("generate_concept", 1);
    });
  });

  describe("Selector hooks", () => {
    it("useRateLimitsData should return rate limit data", () => {
      const { result } = renderHook(() => useRateLimitsData(), {
        wrapper: createWrapper(queryClient),
      });
      expect(result.current).toEqual(mockRateLimitsData);
    });

    it("useRateLimitsLoading should return loading state", () => {
      mockIsLoading = true;
      const { result } = renderHook(() => useRateLimitsLoading(), {
        wrapper: createWrapper(queryClient),
      });
      expect(result.current).toBe(true);
    });

    it("useRateLimitsError should return error state", () => {
      mockError = new Error("Test error");
      const { result } = renderHook(() => useRateLimitsError(), {
        wrapper: createWrapper(queryClient),
      });
      expect(result.current).toBe("Test error");
    });

    it("useRateLimitsRefetch should return refetch function", async () => {
      const { result } = renderHook(() => useRateLimitsRefetch(), {
        wrapper: createWrapper(queryClient),
      });

      // Call the refetch function
      await act(async () => {
        await result.current(true);
      });

      // Should have called the underlying refetch
      expect(refetchMock).toHaveBeenCalled();
    });

    it("useRateLimitsDecrement should return decrementLimit function", async () => {
      const { result } = renderHook(() => useRateLimitsDecrement(), {
        wrapper: createWrapper(queryClient),
      });

      // Call the decrementLimit function
      act(() => {
        result.current("generate_concept", 2);
      });

      // Should have called the underlying decrementLimit
      expect(decrementLimitMock).toHaveBeenCalledWith("generate_concept", 2);
    });
  });

  describe("useRateLimitContext", () => {
    it("should return the complete context object", () => {
      const { result } = renderHook(() => useRateLimitContext(), {
        wrapper: createWrapper(queryClient),
      });

      // Should have all properties
      expect(result.current).toHaveProperty("rateLimits");
      expect(result.current).toHaveProperty("isLoading");
      expect(result.current).toHaveProperty("error");
      expect(result.current).toHaveProperty("refetch");
      expect(result.current).toHaveProperty("decrementLimit");

      // Values should match mock data
      expect(result.current.rateLimits).toEqual(mockRateLimitsData);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(typeof result.current.refetch).toBe("function");
      expect(typeof result.current.decrementLimit).toBe("function");
    });

    it("should respond to changes in the mock data", () => {
      const { result, rerender } = renderHook(() => useRateLimitContext(), {
        wrapper: createWrapper(queryClient),
      });

      // Update mock data
      mockRateLimitsData = {
        ...mockRateLimitsData,
        limits: {
          ...mockRateLimitsData.limits,
          generate_concept: {
            ...mockRateLimitsData.limits.generate_concept,
            remaining: 5,
          },
        },
      };

      // Rerender to pick up changes
      rerender();

      // Context should reflect updated data
      expect(result.current.rateLimits?.limits.generate_concept.remaining).toBe(
        5,
      );
    });
  });
});
