#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run the integration tests for the Filament Consumption Tracker application.
"""

import unittest
import sys
from PyQt5.QtWidgets import QApplication

def run_integration_test():
    """Run the integration tests."""
    print("\n===== Running Filament Consumption Tracker Integration Tests =====\n")
    
    # Ensure we have a QApplication instance before tests run
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_integration.py')
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_integration_test()) 