"""
Run the cost calculation tests.
"""
import unittest
import sys

def run_cost_tests():
    """Run cost calculation tests."""
    # Discover and run tests
    test_loader = unittest.TestLoader()
    
    # Load the specific test modules
    test_suite = unittest.TestSuite()
    test_suite.addTests(test_loader.loadTestsFromName('tests.test_cost_calculation'))
    test_suite.addTests(test_loader.loadTestsFromName('tests.test_cost_analysis_ui'))
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_cost_tests()) 