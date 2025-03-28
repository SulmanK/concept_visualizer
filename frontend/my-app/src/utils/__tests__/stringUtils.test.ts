import { describe, it, expect } from 'vitest';
import { capitalizeFirstLetter, truncateString, toKebabCase } from '../stringUtils';

describe('String Utilities', () => {
  describe('capitalizeFirstLetter', () => {
    it('capitalizes the first letter of a string', () => {
      expect(capitalizeFirstLetter('hello')).toBe('Hello');
      expect(capitalizeFirstLetter('world')).toBe('World');
    });

    it('handles empty strings', () => {
      expect(capitalizeFirstLetter('')).toBe('');
    });

    it('handles strings that are already capitalized', () => {
      expect(capitalizeFirstLetter('Hello')).toBe('Hello');
    });

    it('handles single character strings', () => {
      expect(capitalizeFirstLetter('a')).toBe('A');
    });
  });

  describe('truncateString', () => {
    it('truncates strings longer than the max length', () => {
      expect(truncateString('Hello world', 5)).toBe('Hello...');
    });

    it('does not truncate strings shorter than the max length', () => {
      expect(truncateString('Hello', 10)).toBe('Hello');
    });

    it('handles empty strings', () => {
      expect(truncateString('', 5)).toBe('');
    });

    it('handles strings with exactly the max length', () => {
      expect(truncateString('Hello', 5)).toBe('Hello');
    });
  });

  describe('toKebabCase', () => {
    it('converts space-separated strings to kebab-case', () => {
      expect(toKebabCase('hello world')).toBe('hello-world');
    });

    it('converts camelCase strings to kebab-case', () => {
      expect(toKebabCase('helloWorld')).toBe('hello-world');
    });

    it('converts PascalCase strings to kebab-case', () => {
      expect(toKebabCase('HelloWorld')).toBe('hello-world');
    });

    it('removes special characters', () => {
      expect(toKebabCase('hello@world!')).toBe('helloworld');
    });

    it('handles empty strings', () => {
      expect(toKebabCase('')).toBe('');
    });
  });
}); 