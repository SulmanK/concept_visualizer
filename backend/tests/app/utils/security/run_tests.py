#!/usr/bin/env python
"""Test runner for mask utility tests that allows running the mask utility tests easily."""

import logging
import unittest

from test_mask import TestMaskUtilities

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("test_runner")

    logger.info("Running mask utility tests...")

    # Create a test suite and add the TestMaskUtilities class
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMaskUtilities)

    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Report results
    if result.wasSuccessful():
        logger.info("All tests passed successfully!")
    else:
        logger.error(f"Tests failed! Failures: {len(result.failures)}, Errors: {len(result.errors)}")
