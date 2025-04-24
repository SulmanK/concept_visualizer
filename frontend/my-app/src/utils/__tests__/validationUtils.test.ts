import { describe, it, expect } from "vitest";
import {
  isValidEmail,
  isValidPassword,
  isValidUrl,
  isAlphanumeric,
  isInRange,
} from "../validationUtils";

describe("Validation Utilities", () => {
  describe("isValidEmail", () => {
    it("validates correct email addresses", () => {
      expect(isValidEmail("user@example.com")).toBe(true);
      expect(isValidEmail("firstname.lastname@domain.co.uk")).toBe(true);
      expect(isValidEmail("user+tag@example.com")).toBe(true);
    });

    it("rejects invalid email addresses", () => {
      expect(isValidEmail("")).toBe(false);
      expect(isValidEmail("plainaddress")).toBe(false);
      expect(isValidEmail("@missingusername.com")).toBe(false);
      expect(isValidEmail("user@.com")).toBe(false);
      expect(isValidEmail("user@domain")).toBe(false);
      expect(isValidEmail("user@domain.")).toBe(false);
      expect(isValidEmail("user@.domain.com")).toBe(false);
    });

    it("handles null and undefined inputs", () => {
      expect(isValidEmail(null as any)).toBe(false);
      expect(isValidEmail(undefined as any)).toBe(false);
    });
  });

  describe("isValidPassword", () => {
    it("validates passwords meeting all requirements", () => {
      expect(isValidPassword("Password123!")).toBe(true);
      expect(isValidPassword("Str0ng#P@ssw0rd")).toBe(true);
    });

    it("rejects passwords that are too short", () => {
      expect(isValidPassword("Pw1!")).toBe(false);
      expect(isValidPassword("Pw1!", 10)).toBe(false);
    });

    it("enforces special character requirement when specified", () => {
      expect(isValidPassword("Password123", 8, true)).toBe(false);
      expect(isValidPassword("Password123", 8, false)).toBe(true);
    });

    it("enforces number requirement when specified", () => {
      expect(isValidPassword("Password!", 8, true, true)).toBe(false);
      expect(isValidPassword("Password!", 8, true, false)).toBe(true);
    });

    it("enforces uppercase requirement when specified", () => {
      expect(isValidPassword("password123!", 8, true, true, true)).toBe(false);
      expect(isValidPassword("password123!", 8, true, true, false)).toBe(true);
    });

    it("handles null and undefined inputs", () => {
      expect(isValidPassword(null as any)).toBe(false);
      expect(isValidPassword(undefined as any)).toBe(false);
    });
  });

  describe("isValidUrl", () => {
    it("validates correct URLs", () => {
      expect(isValidUrl("https://www.example.com")).toBe(true);
      expect(isValidUrl("http://example.com/path?query=value")).toBe(true);
      expect(isValidUrl("https://subdomain.example.co.uk/path")).toBe(true);
    });

    it("rejects invalid URLs", () => {
      expect(isValidUrl("")).toBe(false);
      expect(isValidUrl("example.com")).toBe(false);
      expect(isValidUrl("www.example.com")).toBe(false);
      expect(isValidUrl("htp://example.com")).toBe(false);
    });

    it("handles protocol requirement correctly", () => {
      expect(isValidUrl("ftp://example.com", true)).toBe(false);
      expect(isValidUrl("ftp://example.com", false)).toBe(true);
    });

    it("handles null and undefined inputs", () => {
      expect(isValidUrl(null as any)).toBe(false);
      expect(isValidUrl(undefined as any)).toBe(false);
    });
  });

  describe("isAlphanumeric", () => {
    it("validates strings with only alphanumeric characters", () => {
      expect(isAlphanumeric("abc123")).toBe(true);
      expect(isAlphanumeric("ABC123")).toBe(true);
      expect(isAlphanumeric("123")).toBe(true);
      expect(isAlphanumeric("abc")).toBe(true);
    });

    it("rejects strings with non-alphanumeric characters", () => {
      expect(isAlphanumeric("abc-123")).toBe(false);
      expect(isAlphanumeric("abc 123")).toBe(false);
      expect(isAlphanumeric("abc_123")).toBe(false);
    });

    it("handles space allowance correctly", () => {
      expect(isAlphanumeric("abc 123", true)).toBe(true);
      expect(isAlphanumeric("abc 123", false)).toBe(false);
    });

    it("handles empty, null, and undefined inputs", () => {
      expect(isAlphanumeric("")).toBe(false);
      expect(isAlphanumeric(null as any)).toBe(false);
      expect(isAlphanumeric(undefined as any)).toBe(false);
    });
  });

  describe("isInRange", () => {
    it("validates numbers within specified range", () => {
      expect(isInRange(5, 1, 10)).toBe(true);
      expect(isInRange(1, 1, 10)).toBe(true); // Min boundary
      expect(isInRange(10, 1, 10)).toBe(true); // Max boundary
    });

    it("rejects numbers outside specified range", () => {
      expect(isInRange(0, 1, 10)).toBe(false);
      expect(isInRange(11, 1, 10)).toBe(false);
    });

    it("handles invalid inputs", () => {
      expect(isInRange(NaN, 1, 10)).toBe(false);
      expect(isInRange(null as any, 1, 10)).toBe(false);
      expect(isInRange(undefined as any, 1, 10)).toBe(false);
    });
  });
});
