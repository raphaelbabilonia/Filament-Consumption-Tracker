# Filament Consumption Tracker - Developer Guide

This guide provides technical information for developers who want to understand, modify, or contribute to the Filament Consumption Tracker application.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [UI Components](#ui-components)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Adding Features](#adding-features)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### Core Components
- **Database Layer**: SQLAlchemy ORM for database operations
- **UI Layer**: PyQt5 for the graphical interface
- **Business Logic**: Handled in the database handler and UI components
- **Data Visualization**: Matplotlib for charts and graphs

### Design Patterns
- **Model-View Pattern**: Separation of database models and UI
- **Repository Pattern**: Database operations encapsulated in db_handler
- **Factory Pattern**: Used for creating UI components
- **Observer Pattern**: Used for updating UI components when data changes

### Event Flow
1. User interactions trigger UI events
2. UI components call methods in the database handler
3. Database operations are performed
4. Results are returned to UI components
5. UI is updated to reflect changes

## Development Setup

### Prerequisites
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Development Dependencies
- Python 3.7+
- PyQt5
- SQLAlchemy
- Matplotlib
- pandas (for data manipulation)
- pytest (for testing)

### IDE Configuration
Recommended VS Code settings:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

## Project Structure

### Core Modules

#### database/
- `db_handler.py`: Database operations and connection management
- Key classes: `DatabaseHandler`
- Handles all CRUD operations and database transactions

#### models/
- `schema.py`: SQLAlchemy models and database schema
- Key models:
  - `Filament`
  - `Printer`
  - `PrinterComponent`
  - `PrintJob`

#### ui/
- `main_window.py`: Main application window and menu
- `filament_tab.py`: Filament inventory interface
- `printer_tab.py`: Printer management interface
- `print_job_tab.py`: Print job tracking interface
- `reports_tab.py`: Reports and analytics interface

### Key Files

#### main.py
Entry point for the application. Sets up the main window and initializes the database.

#### requirements.txt
Lists all Python dependencies needed for the project.

## Database Schema

### Filament Table
```python
class Filament:
    id: Integer (PK)
    type: String(20)
    color: String(50)
    brand: String(50)
    quantity_remaining: Float
    spool_weight: Float
    price: Float (Nullable)
    purchase_date: DateTime (Nullable)
    last_updated: DateTime
```

### Printer Table
```python
class Printer:
    id: Integer (PK)
    name: String(50)
    model: String(50) (Nullable)
    purchase_date: DateTime (Nullable)
    notes: Text (Nullable)
```

### PrinterComponent Table
```python
class PrinterComponent:
    id: Integer (PK)
    printer_id: Integer (FK)
    name: String(50)
    installation_date: DateTime (Nullable)
    replacement_interval: Float (Nullable)
    usage_hours: Float
    notes: Text (Nullable)
```

### PrintJob Table
```python
class PrintJob:
    id: Integer (PK)
    date: DateTime
    project_name: String(100)
    filament_id: Integer (FK)
    printer_id: Integer (FK)
    filament_used: Float
    duration: Float
    notes: Text (Nullable)
```

### Relationships
- PrintJob → Filament (Many-to-One)
- PrintJob → Printer (Many-to-One)
- PrinterComponent → Printer (Many-to-One)

## UI Components

### Main Window
- Implements `QMainWindow`
- Manages tab widget and menu bar
- Handles application-wide events
- Provides backup and restore functionality

### Tab Implementations
Each tab inherits from `QWidget` and follows a similar pattern:
1. Form for data entry
2. Table for data display
3. Control buttons
4. Optional charts/graphs

### Data Visualization
- Uses Matplotlib for charts
- Embeds charts using `FigureCanvasQTAgg`
- Updates dynamically with data changes
- Multiple chart types supported (bar, pie, line)

### Signal-Slot Connections
The application uses PyQt's signal-slot mechanism for event handling:
- UI signals (button clicks, text changes) are connected to handler methods
- Cross-tab communication is managed through the main window

## Common Issues & Solutions

### Recursive Call Pitfalls
One common issue is recursive calls between methods, particularly in the print_job_tab.py file:

#### Problem
```python
def search_jobs(self):
    # Perform search
    self.apply_filters()  # This calls search_jobs() again!

def apply_filters(self):
    # Apply filters
    self.search_jobs()  # This creates a circular reference
```

#### Solution
```python
def search_jobs(self):
    search_text = self.search_box.text().strip().lower()
    
    # If search box is empty, reload with filters but don't call apply_filters
    if not search_text:
        filament_id = self.filament_filter.currentData()
        printer_id = self.printer_filter.currentData()
        self.load_print_jobs(filament_id=filament_id, printer_id=printer_id)
        return
        
    # Otherwise, apply text filtering directly
    for row in range(self.print_job_table.rowCount()):
        # Filter rows based on content
```

### Other Common Issues

#### Signal Blocking
When updating UI elements that trigger signals, block signals temporarily:
```python
self.combo_box.blockSignals(True)
# Update combo box items
self.combo_box.blockSignals(False)
```

#### Database Connectivity
Handle database transactions in try-except blocks:
```python
try:
    # Perform database operations
    session.commit()
except Exception as e:
    session.rollback()
    # Handle error
finally:
    session.close()
```

#### Memory Management
For large data operations, consider using generators and limiting query results:
```python
# Instead of:
all_items = db_handler.get_all_items()  # Loads everything in memory

# Use:
for batch in db_handler.get_items_in_batches(batch_size=100):
    # Process batch of items
```

## Adding Features

### Adding a New Tab
1. Create new tab class inheriting from `QWidget`
2. Implement `setup_ui()` method
3. Add necessary database operations to `db_handler.py`
4. Register tab in `main_window.py`

### Adding Database Fields
1. Update model in `schema.py`
2. Add corresponding UI elements
3. Update database handler methods
4. Handle data migration for existing databases

### Adding Reports
1. Add new method to `reports_tab.py`
2. Implement data gathering in `db_handler.py`
3. Create visualization using Matplotlib
4. Add UI controls for report parameters

## Testing

### Unit Testing
- Use pytest for testing
- Test database operations in isolation
- Mock database connections
- Test UI components using QTest

### Example Test Structure
```python
def test_add_filament():
    db = DatabaseHandler(':memory:')
    filament_id = db.add_filament(
        type='PLA',
        color='Red',
        brand='Test',
        spool_weight=1000,
        quantity_remaining=1000
    )
    assert filament_id is not None
    filament = db.get_filaments()[0]
    assert filament.type == 'PLA'
```

### UI Testing
```python
def test_search_jobs():
    app = QApplication([])
    tab = PrintJobTab(MockDatabase())
    
    # Simulate typing in search box
    QTest.keyClicks(tab.search_box, "test project")
    
    # Check that filtering was applied
    assert tab.print_job_table.isRowHidden(0) in (True, False)
    app.quit()
```

## Deployment

### Building Executable
Use PyInstaller to create standalone executables:
```bash
pyinstaller --onefile --windowed --icon=app_icon.ico main.py
```

### Configuration
The application looks for a config file in the following locations:
1. Current working directory
2. User's home directory
3. Application directory

### Database Initialization
On first run, the application:
1. Checks for an existing database
2. Creates a new database if none exists
3. Runs any necessary migrations

## Contributing Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document all public methods
- Keep methods focused and single-purpose

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Write tests
4. Update documentation
5. Submit PR with description

### Documentation
- Update relevant documentation files
- Include docstrings for new methods
- Update user guide for UI changes
- Add technical details to developer guide

### Version Control
- Follow semantic versioning
- Use descriptive commit messages
- Reference issue numbers in commits
- Keep commits focused and atomic

## Performance Considerations

### Large Datasets
- Use pagination for large tables
- Implement lazy loading for reports
- Create indices for frequently queried fields

### UI Responsiveness
- Run heavy operations in background threads
- Use QProgressDialog for long-running operations
- Implement cancellation for time-consuming processes

## Security Considerations

### Data Validation
- Validate all user input
- Sanitize data before database operations
- Use prepared statements (handled by SQLAlchemy)

### Error Handling
- Provide user-friendly error messages
- Log detailed errors for debugging
- Don't expose sensitive information in error messages