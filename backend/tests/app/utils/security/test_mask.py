#!/usr/bin/env python
"""
Tests for security masking utilities.
"""

import unittest
import logging
from app.utils.security.mask import (
    mask_credit_card,
    mask_email,
    mask_phone_number
)


class TestMaskUtilities(unittest.TestCase):
    """Test cases for security masking utilities."""

    def setUp(self):
        """Set up test fixtures."""
        # Configure logging for tests
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Setting up test case")

    def test_mask_credit_card(self):
        """Test the mask_credit_card function."""
        test_cases = [
            # Regular credit card numbers
            ("4111111111111111", "************1111"),
            ("5555 5555 5555 4444", "************4444"),
            ("3782-8224-6310-005", "***********0005"),
            
            # Edge cases
            ("41111", "41111"),  # Too short to mask
            ("", ""),  # Empty string
            (None, None),  # None value
        ]
        
        for input_value, expected_output in test_cases:
            with self.subTest(input_value=input_value):
                self.logger.info(f"Testing credit card masking for: {input_value}")
                result = mask_credit_card(input_value)
                self.assertEqual(result, expected_output)

    def test_mask_email(self):
        """Test the mask_email function."""
        test_cases = [
            # Regular email addresses
            ("user@example.com", "u***@example.com"),
            ("john.doe@company.org", "j*******@company.org"),
            ("a.very.long.email@subdomain.example.co.uk", "a****************@subdomain.example.co.uk"),
            
            # Edge cases
            ("a@b.c", "a@b.c"),  # Username too short to mask
            ("notanemail", "notanemail"),  # Not an email format
            ("", ""),  # Empty string
            (None, None),  # None value
        ]
        
        for input_value, expected_output in test_cases:
            with self.subTest(input_value=input_value):
                self.logger.info(f"Testing email masking for: {input_value}")
                result = mask_email(input_value)
                self.assertEqual(result, expected_output)

    def test_mask_phone_number(self):
        """Test the mask_phone_number function."""
        test_cases = [
            # Regular phone numbers
            ("1234567890", "******7890"),
            ("(123) 456-7890", "******7890"),
            ("+1 (123) 456-7890", "*******7890"),
            
            # Edge cases
            ("123456", "123456"),  # Too short to mask
            ("", ""),  # Empty string
            (None, None),  # None value
        ]
        
        for input_value, expected_output in test_cases:
            with self.subTest(input_value=input_value):
                self.logger.info(f"Testing phone number masking for: {input_value}")
                result = mask_phone_number(input_value)
                self.assertEqual(result, expected_output)

    def tearDown(self):
        """Clean up after each test."""
        self.logger.info("Tearing down test case")


if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(level=logging.INFO)
    unittest.main() 