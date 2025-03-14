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
10.   [Contributing Guidelines](#contributing-guidelines)
11.   [Cloud Sync and Multi-Device Support](#cloud-sync-and-multi-device-support)

## Architecture Overview

For a comprehensive overview of the application architecture, please refer to the [Application Structure](application_structure.md) document, which covers:

-  Directory structure and code organization
-  Core modules and their responsibilities
-  Data flow and processing
-  UI architecture and components
-  Database architecture and relationships
-  Testing framework

This section provides a summary of the key architectural components.

### Core Components

-  **Database Layer**: SQLAlchemy ORM for database operations
-  **UI Layer**: PyQt5 for the graphical interface
-  **Business Logic**: Handled in the database handler and UI components
-  **Data Visualization**: Matplotlib for charts and graphs

### Design Patterns

-  **Model-View Pattern**: Separation of database models and UI
-  **Repository Pattern**: Database operations encapsulated in db_handler
-  **Factory Pattern**: Used for creating UI components
-  **Observer Pattern**: Used for updating UI components when data changes

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

-  Python 3.7+
-  PyQt5
-  SQLAlchemy
-  Matplotlib
-  pandas (for data manipulation)
-  pytest (for testing)

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

-  `db_handler.py`: Database operations and connection management
-  Key classes: `DatabaseHandler`
-  Handles all CRUD operations and database transactions

#### models/

-  `schema.py`: SQLAlchemy models and database schema
-  Key models:
   -  `Filament`
   -  `Printer`
   -  `PrinterComponent`
   -  `PrintJob`

#### ui/

-  `main_window.py`: Main application window and menu
-  `filament_tab.py`: Filament inventory interface
-  `printer_tab.py`: Printer management interface
-  `print_job_tab.py`: Print job tracking interface
-  `reports_tab.py`: Reports and analytics interface

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

### FilamentIdealInventory Table

```python
class FilamentIdealInventory:
    id: Integer (PK)
    type: String(20)
    color: String(50)
    brand: String(50)
    ideal_quantity: Float
```

### FilamentLinkGroup Table

```python
class FilamentLinkGroup:
    id: Integer (PK)
    name: String(100)
    description: Text (Nullable)
    ideal_quantity: Float
```

### FilamentLink Table

```python
class FilamentLink(Base):
    """Table for storing linked filaments within a group."""
    __tablename__ = 'filament_links'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('filament_link_groups.id'), nullable=False)
    type = Column(String(20), nullable=False)  # PLA, ABS, etc.
    color = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)

    # Relationship with group
    group = relationship("FilamentLinkGroup", back_populates="filament_links")
```

### AppSettings Table

```python
class AppSettings(Base):
    """Table for storing application settings."""
    __tablename__ = 'app_settings'

    id = Column(Integer, primary_key=True)
    setting_key = Column(String(50), nullable=False, unique=True)
    setting_value = Column(String(255), nullable=False)
```

The AppSettings table is used to store global application settings such as the electricity cost per kWh. Settings are stored as key-value pairs.

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

-  PrintJob → Filament (Many-to-One)
-  PrintJob → Printer (Many-to-One)
-  PrinterComponent → Printer (Many-to-One)
-  FilamentLink → FilamentLinkGroup (Many-to-One)

## Key Components

### Filament Link Groups

#### Implementation Details

Filament Link Groups are implemented using two main tables:

-  `FilamentLinkGroup`: Stores group metadata (name, description, ideal quantity)
-  `FilamentLink`: Maps filaments to groups using type, color, and brand (composite key matching)

The system is designed to:

1. Allow filaments to be logically grouped while maintaining individual records
2. Present combined status and statistics in the UI
3. Apply ideal quantities at the group level

#### Key Methods in DatabaseHandler

```python
# Creating and managing groups
create_filament_link_group(name, description=None, ideal_quantity=0)
update_filament_link_group(group_id, name=None, description=None, ideal_quantity=None)
delete_filament_link_group(group_id)

# Managing filament associations
add_filament_to_link_group(group_id, filament_type, color, brand)
remove_filament_from_link_group(group_id, filament_type, color, brand)

# Retrieving group data
get_filament_link_groups()
get_filament_link_group(group_id)

# Global settings management
get_setting(key, default=None)              # Get a setting value by key
set_setting(key, value)                     # Set a setting value by key
get_electricity_cost()                      # Get the global electricity cost per kWh
set_electricity_cost(cost)                  # Set the global electricity cost per kWh
```

#### Inventory Status Algorithm

The `get_inventory_status()` method in `DatabaseHandler` builds the combined inventory view by:

1. Processing all link groups first
2. Calculating combined quantities for each group
3. Creating virtual entries for groups in the results
4. Marking filaments as "processed" to avoid duplication
5. Then adding individual filaments that aren't in any group

### Ideal Quantity Preservation

#### Core Implementation

The system uses multiple mechanisms to ensure ideal quantities aren't lost during operations:

1. **Capture and Apply Pattern**:

   ```python
   # Before operation
   preserved_quantities = capture_current_ideal_quantities()

   # Perform operation (create/delete group, etc.)

   # After operation
   refresh_inventory_status(preserved_quantities)
   ```

2. **Double-Source Value Collection**:
   The `capture_current_ideal_quantities()` method collects values from both:

   -  The UI table (current visual state)
   -  The database (persisted values)

   This creates redundancy to prevent data loss.

3. **Zero Detection and Repair**:
   The `fix_zero_ideal_quantities()` method scans for and repairs any quantities
   that were inadvertently set to zero.

#### Case-Insensitive Matching

To improve robustness, the system implements case-insensitive matching for filament identification:

```python
# Simplified example from code
for p_key, p_value in preserved_ideal_quantities.items():
    if (p_key[0].upper() == item['type'].upper() and
        p_key[1].upper() == item['color'].upper() and
        p_key[2].upper() == item['brand'].upper()):
        # Match found, apply preserved value
```

### Color Coding System

#### Color Calculation

The color coding system uses a centralized method to ensure consistency:

```python
def _get_status_color(self, percentage):
    """Get the appropriate color for a given percentage."""
    if percentage is None:
        return QColor(240, 240, 240)  # Light Gray for "No Target Set"
    elif percentage == 0:
        return QColor(255, 200, 200)  # Very Light Red for "Out of Stock"
    elif percentage < 20:
        return QColor(255, 200, 200)  # Very Light Red for "Critical - Order Now"
    elif percentage < 50:
        return QColor(255, 220, 180)  # Very Light Orange for "Low - Order Soon"
    elif percentage < 95:
        return QColor(255, 250, 200)  # Very Light Yellow for "Adequate"
    elif percentage < 120:
        return QColor(200, 255, 200)  # Very Light Green for "Optimal"
    else:
        return QColor(230, 210, 255)  # Very Light Purple for "Overstocked"
```

#### Row-Based Coloring

To ensure consistent coloring across all cells in a row, a row-based coloring approach is used:

```python
def _apply_colors_to_row(self, row, percentage, is_group=False):
    """Apply color coding to an entire row based on percentage."""
    # Get base color based on percentage
    base_color = self._get_status_color(percentage)

    # For groups, make the color slightly darker to distinguish them
    if is_group:
        base_color = base_color.darker(110)  # 10% darker

    # Apply color to all cells in the row
    for col in range(7):
        table_item = self.status_table.item(row, col)
        if table_item:  # Make sure item exists before applying color
            table_item.setBackground(base_color)
```

This ensures:

1. Consistent coloring across all columns in a row
2. Visual distinction between group and individual entries
3. Centralized color logic for easier maintenance

## UI Components

### Main Window

-  Implements `QMainWindow`
-  Manages tab widget and menu bar
-  Handles application-wide events
-  Provides backup and restore functionality

### Tab Implementations

Each tab inherits from `QWidget` and follows a similar pattern:

1. Form for data entry
2. Table for data display
3. Control buttons
4. Optional charts/graphs

### Data Visualization

-  Uses Matplotlib for charts
-  Embeds charts using `FigureCanvasQTAgg`
-  Updates dynamically with data changes
-  Multiple chart types supported (bar, pie, line)

### Signal-Slot Connections

The application uses PyQt's signal-slot mechanism for event handling:

-  UI signals (button clicks, text changes) are connected to handler methods
-  Cross-tab communication is managed through the main window

### Print Job Tab

The print job tracking interface is implemented in `print_job_tab.py` and includes the following key features:

#### Filament Selection

-  Primary filament selection displays filament IDs for easy identification
-  The filament display format is: `"Brand Color Type - ID:X (remaining quantity)"`
-  Secondary filaments use the same display format for consistency

#### Multicolor Print Support

-  Implemented using a dynamic interface that adjusts based on user needs
-  The `toggle_multicolor`
