import { describe, it, expect } from "vitest";
import {
  formatDate,
  formatCurrency,
  formatNumber,
  formatFileSize,
} from "../formatUtils";

describe("Format Utilities", () => {
  describe("formatDate", () => {
    it("formats dates correctly", () => {
      const date = new Date(2023, 0, 15); // Jan 15, 2023
      expect(formatDate(date)).toBe("Jan 15, 2023");
    });

    it("handles different locales", () => {
      const date = new Date(2023, 0, 15);
      // This will vary based on the locale, but we can at least check it's different
      expect(formatDate(date, "de-DE")).not.toBe(formatDate(date, "en-US"));
    });

    it("returns empty string for invalid dates", () => {
      const invalidDate = new Date("invalid date");
      expect(formatDate(invalidDate)).toBe("");
      expect(formatDate(null as any)).toBe("");
      expect(formatDate(undefined as any)).toBe("");
    });
  });

  describe("formatCurrency", () => {
    it("formats USD currency correctly", () => {
      expect(formatCurrency(1000)).toBe("$1,000.00");
      expect(formatCurrency(1234.56)).toBe("$1,234.56");
      expect(formatCurrency(0)).toBe("$0.00");
    });

    it("handles different currencies", () => {
      expect(formatCurrency(1000, "EUR", "en-US")).toBe("€1,000.00");
      expect(formatCurrency(1000, "GBP", "en-US")).toBe("£1,000.00");
      expect(formatCurrency(1000, "JPY", "en-US")).toBe("¥1,000");
    });

    it("returns empty string for invalid amounts", () => {
      expect(formatCurrency(NaN)).toBe("");
      expect(formatCurrency(null as any)).toBe("");
      expect(formatCurrency(undefined as any)).toBe("");
    });
  });

  describe("formatNumber", () => {
    it("formats numbers with correct decimal places", () => {
      expect(formatNumber(1000)).toBe("1,000.00");
      expect(formatNumber(1234.56789, 3)).toBe("1,234.568");
      expect(formatNumber(0.5, 1)).toBe("0.5");
    });

    it("handles different locales", () => {
      // In many European countries, commas and periods are swapped in numbers
      const formattedEuro = formatNumber(1234.56, 2, "de-DE");
      expect(formattedEuro).toContain("1.234,56");
    });

    it("returns empty string for invalid numbers", () => {
      expect(formatNumber(NaN)).toBe("");
      expect(formatNumber(null as any)).toBe("");
      expect(formatNumber(undefined as any)).toBe("");
    });
  });

  describe("formatFileSize", () => {
    it("formats file sizes correctly", () => {
      expect(formatFileSize(0)).toBe("0 Bytes");
      expect(formatFileSize(1024)).toBe("1 KB");
      expect(formatFileSize(1024 * 1024)).toBe("1 MB");
      expect(formatFileSize(1024 * 1024 * 1024)).toBe("1 GB");
    });

    it("handles decimal precision", () => {
      expect(formatFileSize(1536, 1)).toBe("1.5 KB");
      expect(formatFileSize(1536, 0)).toBe("2 KB");
      expect(formatFileSize(2.5 * 1024 * 1024, 2)).toBe("2.50 MB");
    });

    it("returns empty string for invalid sizes", () => {
      expect(formatFileSize(-1024)).toBe("");
      expect(formatFileSize(NaN)).toBe("");
      expect(formatFileSize(null as any)).toBe("");
      expect(formatFileSize(undefined as any)).toBe("");
    });
  });
});
