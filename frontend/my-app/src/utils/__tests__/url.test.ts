import { vi, describe, it, expect, beforeEach } from "vitest";
import { extractStoragePathFromUrl } from "../url";
import { logger } from "../logger";

// Mock the logger
vi.mock("../logger", () => ({
  logger: {
    debug: vi.fn(),
    error: vi.fn(),
  },
}));

describe("URL Utils", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("extractStoragePathFromUrl", () => {
    it("should return null for undefined input", () => {
      const result = extractStoragePathFromUrl(undefined);
      expect(result).toBeNull();
    });

    it("should return null for empty input", () => {
      const result = extractStoragePathFromUrl("");
      expect(result).toBeNull();
    });

    it("should extract path from concept-images URL", () => {
      const url =
        "https://project-id.supabase.co/storage/v1/object/public/concept-images/user-id/image-id.png";
      const result = extractStoragePathFromUrl(url);
      expect(result).toBe("user-id/image-id.png");
      expect(logger.debug).toHaveBeenCalledWith(expect.any(String), url);
    });

    it("should extract path from palette-images URL", () => {
      const url =
        "https://project-id.supabase.co/storage/v1/object/public/palette-images/user-id/image-id.png";
      const result = extractStoragePathFromUrl(url);
      expect(result).toBe("user-id/image-id.png");
      expect(logger.debug).toHaveBeenCalledWith(expect.any(String), url);
    });

    it("should extract path from signed URL with URL parameter", () => {
      const url =
        "https://project-id.supabase.co/storage/v1/object/sign/concept-images?url=bucket-name/user-id/image-id.png";
      const result = extractStoragePathFromUrl(url);
      expect(result).toBe("user-id/image-id.png");
    });

    it("should extract path from direct storage path pattern", () => {
      const url = "https://some-domain.com/some-path/user-id/image-id.png";
      const result = extractStoragePathFromUrl(url);
      expect(result).toBe("user-id/image-id.png");
    });

    it("should extract path from URL with query parameters", () => {
      const url =
        "https://some-domain.com/some-path/user-id/image-id.png?token=abc123";
      const result = extractStoragePathFromUrl(url);
      expect(result).toBe("user-id/image-id.png");
    });

    it("should handle invalid URLs gracefully", () => {
      const invalidUrl = "not a valid url";
      const result = extractStoragePathFromUrl(invalidUrl);
      expect(result).toBeNull();
      expect(logger.error).toHaveBeenCalled();
    });
  });
});
