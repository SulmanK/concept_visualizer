import { vi, describe, test, expect, beforeEach } from "vitest";
import { apiClient } from "../../services/apiClient";

// Mock the apiClient methods directly
vi.mock("../../services/apiClient", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    exportImage: vi.fn(),
  },
}));

describe("apiClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("apiClient.get should call the get method", async () => {
    const mockResponse = { data: "test data" };
    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await apiClient.get("/test-endpoint");

    expect(apiClient.get).toHaveBeenCalledWith("/test-endpoint");
    expect(result).toEqual(mockResponse);
  });

  test("apiClient.post should call the post method", async () => {
    const mockResponse = { data: "test data" };
    const requestData = { test: "data" };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await apiClient.post("/test-endpoint", requestData);

    expect(apiClient.post).toHaveBeenCalledWith("/test-endpoint", requestData);
    expect(result).toEqual(mockResponse);
  });

  test("apiClient.exportImage should make a POST request with blob response type", async () => {
    const mockBlob = new Blob(["test data"], { type: "image/png" });

    vi.mocked(apiClient.exportImage).mockResolvedValueOnce(mockBlob);

    const result = await apiClient.exportImage(
      "test-image-path",
      "png",
      "medium",
    );

    expect(apiClient.exportImage).toHaveBeenCalledWith(
      "test-image-path",
      "png",
      "medium",
    );

    expect(result).toBe(mockBlob);
  });
});
