#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test runner for Filament Consumption Tracker.
This script can run all tests or specific test patterns.
"""
import unittest
import sys
import argparse
from PyQt5.QtWidgets import QApplication

def run_tests(pattern=None):
    """
    Run tests matching the specified pattern.
    
    Args:
        pattern: Optional pattern to match test files (e.g., 'test_db*.py')
                If None, all tests will be run.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Ensure we have a QApplication instance before tests run
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    
    if pattern:
        print(f"\n===== Running tests matching '{pattern}' =====\n")
        test_suite = test_loader.discover('tests', pattern=pattern)
    else:
        print("\n===== Running all tests =====\n")
        test_suite = test_loader.discover('tests')
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run tests for Filament Consumption Tracker')
    parser.add_argument('--pattern', '-p', type=str, help='Pattern to match test files (e.g., test_db*.py)')
    
    args = parser.parse_args()
    
    return run_tests(args.pattern)

if __name__ == "__main__":
    sys.exit(main()) 