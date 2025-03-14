#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive test runner for Filament Consumption Tracker.
This script runs all available tests and reports results.
"""

import unittest
import sys
import os
import time
from PyQt5.QtWidgets import QApplication

def run_all_tests():
    """Run all tests for the Filament Consumption Tracker application."""
    start_time = time.time()
    print("\n===== Running Filament Consumption Tracker Test Suite =====\n")
    
    # Ensure we have a QApplication instance before tests run
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    
    # First run non-UI tests (faster and more reliable)
    print("\n----- Running Database Tests -----\n")
    db_suite = test_loader.discover('tests', pattern='test_db*.py')
    db_result = unittest.TextTestRunner(verbosity=2).run(db_suite)
    
    print("\n----- Running Schema Tests -----\n")
    schema_suite = test_loader.discover('tests', pattern='test_schema.py')
    schema_result = unittest.TextTestRunner(verbosity=2).run(schema_suite)
    
    print("\n----- Running Cost Calculation Tests -----\n")
    cost_suite = test_loader.discover('tests', pattern='test_cost*.py')
    cost_result = unittest.TextTestRunner(verbosity=2).run(cost_suite)
    
    # Then run UI tests
    print("\n----- Running UI Tests -----\n")
    ui_suite = test_loader.discover('tests', pattern='test_ui.py')
    ui_result = unittest.TextTestRunner(verbosity=2).run(ui_suite)
    
    print("\n----- Running Application Tests -----\n")
    app_suite = test_loader.discover('tests', pattern='test_app.py')
    app_result = unittest.TextTestRunner(verbosity=2).run(app_suite)
    
    print("\n----- Running Integration Tests -----\n")
    integration_suite = test_loader.discover('tests', pattern='test_integration.py')
    integration_result = unittest.TextTestRunner(verbosity=2).run(integration_suite)
    
    # Compile results
    all_successful = (
        db_result.wasSuccessful() and
        schema_result.wasSuccessful() and
        cost_result.wasSuccessful() and
        ui_result.wasSuccessful() and
        app_result.wasSuccessful() and
        integration_result.wasSuccessful()
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Report summary
    print(f"\n===== Test Suite Completed in {duration:.2f} seconds =====")
    
    if all_successful:
        print("\nAll tests PASSED! ✅")
    else:
        print("\nSome tests FAILED! ❌")
        
        # Summarize failures by test category
        if not db_result.wasSuccessful():
            print(f"- Database Tests: {len(db_result.failures) + len(db_result.errors)} failed")
        if not schema_result.wasSuccessful():
            print(f"- Schema Tests: {len(schema_result.failures) + len(schema_result.errors)} failed")
        if not cost_result.wasSuccessful():
            print(f"- Cost Calculation Tests: {len(cost_result.failures) + len(cost_result.errors)} failed")
        if not ui_result.wasSuccessful():
            print(f"- UI Tests: {len(ui_result.failures) + len(ui_result.errors)} failed")
        if not app_result.wasSuccessful():
            print(f"- Application Tests: {len(app_result.failures) + len(app_result.errors)} failed")
        if not integration_result.wasSuccessful():
            print(f"- Integration Tests: {len(integration_result.failures) + len(integration_result.errors)} failed")
    
    print("\n============================================")
    
    # Return exit code based on test results
    return 0 if all_successful else 1

if __name__ == "__main__":
    sys.exit(run_all_tests()) 