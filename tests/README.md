# Filament Consumption Tracker Tests

This directory contains tests for the Filament Consumption Tracker application.

## Test File Structure

### Unit Tests

-  `test_db_handler.py`: Tests for database operations and the DatabaseHandler class
-  `test_schema.py`: Tests for database schema models and relationships
-  `test_cost_calculation.py`: Tests for cost calculation logic and algorithms

### UI Tests

-  `test_ui.py`: Basic tests for UI components and their initialization
-  `test_cost_analysis_ui.py`: Tests for the cost analysis UI components

### Integration Tests

-  `test_app.py`: Tests for the main application functionality
-  `test_integration.py`: Comprehensive integration tests covering all major features

## Test Runner Scripts

The repository includes several test runner scripts:

-  `run_tests.py`: Flexible test runner that can run specific test patterns
-  `run_all_tests.py`: Runs all tests in a specific order (non-UI tests first)
-  `run_integration_test.py`: Runs just the integration tests
-  `run_cost_tests.py`: Runs just the cost calculation tests

## Running Tests

### Run All Tests

To run all tests:

```bash
python run_all_tests.py
```

This will run all tests in a specific order, with non-UI tests first (faster and more reliable) followed by UI tests. The test run output includes:

-  Database tests
-  Schema tests
-  Cost calculation tests
-  UI tests
-  Application tests
-  Integration tests

### Run Specific Tests

To run tests matching a specific pattern:

```bash
python run_tests.py -p test_db*.py  # Run all database tests
python run_tests.py -p test_schema.py  # Run schema tests
python run_tests.py -p test_integration.py  # Run integration tests
```

This is useful for focusing on specific components during development.

### Run Integration Tests

To run just the integration tests:

```bash
python run_integration_test.py
```

Integration tests verify that all components work together as expected and cover real-world usage scenarios.

### Run Cost Calculation Tests

To run just the cost calculation tests:

```bash
python run_cost_tests.py
```

## Creating Test Data

For manual testing, you can populate the database with test data:

```bash
python create_test_data.py
```

This script will:

1. Create a variety of filaments with different types, colors, and brands
2. Set ideal quantities for some filament combinations
3. Create filament link groups with relationships
4. Add printers with various specifications
5. Create print jobs with different characteristics

You'll be prompted whether to clear existing data before adding test data.

## Test Database Handling

Most tests use an in-memory or temporary SQLite database to avoid affecting your production data. The test database is:

-  Created at the start of the test
-  Populated with test data
-  Used during test execution
-  Deleted after the test completes

## Writing New Tests

When writing new tests:

1. Follow the naming convention: `test_*.py`
2. Inherit from `unittest.TestCase`
3. Use descriptive test method names prefixed with `test_`
4. Add setup and teardown methods as needed
5. Use assertions to verify expected behavior

Example:

```python
import unittest

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        # Setup code
        self.db_handler = DatabaseHandler(':memory:')

    def test_my_feature(self):
        # Test code
        result = self.db_handler.some_method()
        self.assertEqual(expected_value, result)

    def tearDown(self):
        # Cleanup code
        self.db_handler.close_connection()
```

## Testing UI Components

When testing UI components:

1. Ensure you have a QApplication instance before any UI tests
2. Mock user interactions using QTest methods
3. Override message boxes and dialogs to prevent user interaction during tests
4. Use a separate test database

Example:

```python
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Create a QApplication instance
app = QApplication.instance() or QApplication([])

# Test a button click
QTest.mouseClick(button, Qt.LeftButton)

# Test entering text
QTest.keyClicks(line_edit, "test text")
```

## Test Dependencies

The tests require the following dependencies:

-  PyQt5: For UI component testing
-  SQLAlchemy: For database operations
-  Other dependencies as specified in requirements.txt
