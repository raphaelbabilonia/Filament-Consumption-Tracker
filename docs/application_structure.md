# Filament Consumption Tracker - Application Structure

This document provides a comprehensive overview of the Filament Consumption Tracker application's architecture, code organization, and technical details.

## Table of Contents

1. [Application Overview](#application-overview)
2. [Technology Stack](#technology-stack)
3. [Directory Structure](#directory-structure)
4. [Core Modules](#core-modules)
5. [Data Flow](#data-flow)
6. [UI Architecture](#ui-architecture)
7. [Database Architecture](#database-architecture)
8. [Testing Framework](#testing-framework)
9. [Cloud Sync Implementation](#cloud-sync-implementation)

## Application Overview

The Filament Consumption Tracker is a desktop application designed for 3D printing enthusiasts to:

-  Track filament inventory and usage
-  Manage multiple 3D printers and their components
-  Record and analyze print jobs
-  Generate reports and visualize data
-  Sync data across multiple devices

The application uses a three-tier architecture:

1. **Presentation Layer**: UI components built with PyQt5
2. **Business Logic Layer**: Implemented in the UI controllers and database handler
3. **Data Layer**: SQLite database with SQLAlchemy ORM

## Technology Stack

The application is built using the following technologies:

-  **Python**: Core programming language (3.7+)
-  **PyQt5**: GUI framework for desktop application development
-  **SQLAlchemy**: ORM (Object-Relational Mapping) for database operations
-  **SQLite**: Local database engine
-  **Matplotlib**: Data visualization for reports and charts
-  **Google Drive API**: Cloud synchronization capability

## Directory Structure

The application's codebase is organized into the following main directories:

```
filament-consumption-tracker/
├── database/                # Database access layer
│   └── db_handler.py        # Database operations handler
├── models/                  # Data models
│   └── schema.py            # SQLAlchemy ORM models
├── ui/                      # User interface components
│   ├── filament_tab.py      # Filament inventory management UI
│   ├── printer_tab.py       # Printer management UI
│   ├── print_job_tab.py     # Print job tracking UI
│   ├── reports_tab.py       # Reports and analytics UI
│   ├── main_window.py       # Main application window
│   ├── drive_backup_dialog.py  # Google Drive backup dialog
│   └── google_drive_utils.py   # Google Drive integration utilities
├── docs/                    # Documentation
├── tests/                   # Test suite
├── main.py                  # Application entry point
├── requirements.txt         # Project dependencies
└── README.md                # Project overview
```

## Core Modules

### 1. Database Handler (`database/db_handler.py`)

The DatabaseHandler class serves as the central interface to the database, implementing the Repository pattern. It provides methods for:

-  CRUD operations for all entity types (filaments, printers, print jobs, etc.)
-  Transaction management
-  Complex queries for aggregated data
-  Database maintenance operations
-  Data import/export functionality

Key methods include:

-  `add_filament()`, `update_filament()`, `delete_filament()`
-  `add_printer()`, `add_printer_component()`
-  `add_print_job()`
-  `get_aggregated_filament_inventory()`
-  `get_inventory_status()`
-  `create_filament_link_group()`, `add_filament_to_link_group()`

### 2. Data Models (`models/schema.py`)

The data models are defined using SQLAlchemy ORM and include:

-  `Filament`: Represents a filament spool with type, color, brand, weight, etc.
-  `Printer`: Represents a 3D printer with model, name, purchase info, etc.
-  `PrinterComponent`: Components of printers like nozzles, belts, etc.
-  `PrintJob`: A record of a print job with material used, duration, etc.
-  `FilamentLinkGroup`: A group of related filaments for inventory management
-  `FilamentLink`: Association between filaments and filament groups
-  `FilamentIdealInventory`: Desired stock levels for specific filament types
-  `AppSettings`: Application-wide settings like electricity costs

These models define the database schema and relationships between entities.

### 3. UI Components (`ui/`)

The UI is organized into tabs, each handling a specific feature set:

#### Main Window (`main_window.py`)

-  Creates and manages the application window and tab layout
-  Handles global application events and menu actions
-  Manages application state and session
-  Coordinates between different UI components
-  Implements backup, restore, and cloud sync functionality

#### Filament Tab (`filament_tab.py`)

-  Displays filament inventory in tabular form
-  Provides interfaces for adding, editing, and deleting filaments
-  Shows aggregated inventory by filament type/color
-  Displays inventory status with color-coded alerts
-  Manages filament link groups for related filaments

#### Printer Tab (`printer_tab.py`)

-  Lists printers with details
-  Manages printer components and maintenance
-  Tracks component replacement schedules
-  Records printer usage statistics
-  Provides complete component editing functionality
-  Supports resetting usage hours after maintenance

#### Print Job Tab (`print_job_tab.py`)

-  Records new print jobs with filament usage
-  Associates jobs with printers and filaments
-  Tracks usage history with detailed filtering
-  Provides template functionality for recurring jobs

#### Reports Tab (`reports_tab.py`)

-  Generates reports on material usage, costs, and printer utilization
-  Visualizes data with charts and graphs
-  Provides customizable date ranges for analysis
-  Calculates cost metrics for printing projects

### 4. Cloud Sync (`ui/google_drive_utils.py` and `ui/drive_backup_dialog.py`)

These modules implement the Google Drive integration for cloud backup and sync:

-  Authentication with Google OAuth 2.0
-  Automatic folder creation and management
-  File upload and download operations
-  Synchronization logic between devices
-  Conflict resolution for concurrent changes

## Data Flow

The application follows this typical data flow:

1. **User Interface Event**: User interacts with the UI (e.g., clicks "Add Filament")
2. **UI Controller Action**: The relevant UI component processes the event (e.g., `filament_tab.add_filament()`)
3. **Database Operation**: The UI controller calls the appropriate DatabaseHandler method (e.g., `db_handler.add_filament()`)
4. **Database Transaction**: The DatabaseHandler executes the SQL operations using SQLAlchemy
5. **Result Processing**: The result is returned to the UI controller
6. **UI Update**: The UI is refreshed to show the changes (e.g., reloading the filament table)

## UI Architecture

The UI follows a controller-based architecture where each tab acts as a controller for its specific feature set:

1. **MainWindow**: Parent container and application coordinator
2. **Tab Classes**: Feature-specific controllers (FilamentTab, PrinterTab, etc.)
3. **Dialog Classes**: Modal interfaces for specific operations (FilamentDialog, FilamentLinkGroupDialog, etc.)

The UI uses PyQt5's signals and slots mechanism for event handling:

-  UI components emit signals when events occur
-  Slot methods are connected to these signals to handle the events
-  Custom signals are defined for complex operations

## Database Architecture

The application uses a SQLite database with SQLAlchemy ORM:

1. **ORM Models**: Define the database schema and relationships (`models/schema.py`)
2. **DatabaseHandler**: Provides a high-level API for database operations
3. **Session Management**: Handles database transactions and connection pooling

Key database features include:

-  One-to-many relationships (e.g., Printer to PrinterComponents)
-  Many-to-many relationships (e.g., Filaments to FilamentLinkGroups via FilamentLink)
-  Cascade operations for maintaining referential integrity
-  Lazy loading for efficient query execution

The database file is stored in the user's Documents folder for easy backup and portability.

## Testing Framework

The application includes a comprehensive testing framework:

-  **Unit Tests**: Test individual components in isolation
-  **Integration Tests**: Test the interaction between components
-  **UI Tests**: Test the user interface components
-  **Test Runners**: Scripts for running different test suites

The tests use a separate in-memory or temporary database to avoid affecting production data.

## Cloud Sync Implementation

The cloud sync functionality uses Google Drive API for storing and syncing database backups:

1. **Authentication**: OAuth 2.0 flow for secure access to Google Drive
2. **Backup**: Creates a database backup and uploads it to Google Drive
3. **Sync**: Detects and resolves conflicts between different device backups
4. **Restore**: Downloads and restores database from Google Drive backup

The sync process is optimized for:

-  Small database files (direct upload)
-  Large database files (chunked upload)
-  Network reliability (retry logic)
-  User experience (background operations with progress tracking)

The application tracks sync status and provides visual indicators for unsaved changes.

---

This document provides a high-level overview of the application structure. For more detailed information about specific components, please refer to the inline documentation in the code or contact the development team.
