# Filament Consumption Tracker

A comprehensive desktop application for 3D printing enthusiasts to track filament usage, manage printer maintenance, and analyze printing costs.

## Features

-  **Filament Inventory Management**

   -  Track multiple filament types, colors, and brands
   -  Monitor remaining quantities with low stock alerts
   -  Purchase history and cost tracking
   -  Detailed usage statistics
   -  Aggregated inventory view by filament type/color combinations

-  **Print Job Tracking**

   -  Record print jobs with material usage and duration
   -  Associate jobs with specific printers and filaments
   -  Project-based organization
   -  Comprehensive print history
   -  Powerful search and filter system
   -  Use existing jobs as templates for new ones via right-click functionality

-  **Printer Management**

   -  Maintain printer inventory with detailed information
   -  Track printer components and maintenance schedules
   -  Component replacement reminders based on usage
   -  Usage statistics and maintenance history

-  **Reports and Analytics**

   -  Material usage analysis by type, color, and printer
   -  Cost tracking and analysis
   -  Printer utilization statistics
   -  Component maintenance schedules
   -  Visual data representation with charts
   -  Customizable date ranges

-  **Cloud Sync and Multi-Device Support**

   -  Automatic synchronization with Google Drive
   -  Configurable sync frequency (on exit, hourly, daily)
   -  Smart backup management with customizable retention
   -  Sync status tracking with timestamps
   -  Seamless multi-device workflow
   -  Unsaved changes detection and handling

-  **Data Management**
   -  Built-in local backup and restore functionality
   -  Google Drive cloud backup integration with backup-on-exit feature
   -  Automatic sync across multiple devices
   -  Optimized upload process for small and large databases
   -  Easy-to-use restore functionality
   -  Data export to CSV format
   -  Automatic database versioning

## Recent Updates

### Version 1.5.0

-  **Cloud Sync and Multi-Device Support**
   -  Added dedicated Sync Settings dialog
   -  Implemented automatic sync with configurable frequency
   -  Added maximum backup limit to manage storage space
   -  Added unsaved changes detection with visual indicators
   -  Created comprehensive multi-device workflow support
   -  Added Sync Now button for immediate synchronization

### Version 1.4.2

-  **Template Feature for Print Jobs**
   -  Added right-click functionality to print job history table
   -  Use existing print jobs as templates for new ones
   -  Quickly duplicate project settings, filament selections, and durations

### Version 1.4.1

-  **Optimized Cloud Backup System**
   -  Improved upload speeds with smart file size detection
   -  Added direct upload for small databases (<5MB) for faster backups
   -  Enhanced chunked upload with 5MB chunks for larger databases
   -  Implemented automatic retry logic for network issues
   -  Added backup-on-exit dialog with progress tracking
   -  Fixed UI responsiveness during backup operations
   -  Improved error handling and recovery

### Version 1.4.0

-  **Cloud Backup Integration**

   -  Added Google Drive integration for cloud backup/restore
   -  Secure authentication using OAuth 2.0
   -  Automatic folder creation and management
   -  Easy-to-use interface for cloud operations
   -  Comprehensive setup documentation

-  **Enhanced Database Management**
   -  Reorganized backup/restore menu for better usability
   -  Added clear separation between local and cloud backup options
   -  Improved database reconnection after restore operations
   -  Enhanced error handling for backup/restore operations

### Version 1.3.0

-  **Enhanced Print Job Management**
   -  Added filament ID display to make spool identification easier
   -  Improved multicolor print job tracking with configurable number of additional filaments (1-3)
   -  Updated print duration input format to more intuitive hours and minutes (e.g., 2h 30m)
   -  Enhanced date display format in print job history (dd/mm/yy)
   -  Streamlined user interface by removing redundant "Amount Used" labels
-  **UI Improvements**
   -  Better organization of multicolor print fields for easier tracking
   -  Improved visibility control for secondary filament fields
   -  Fixed issues with date display and sorting in print job history
   -  Enhanced error handling in the multicolor print interface

### Version 1.2.0

-  **Enhanced Filament Inventory Management**

   -  Added filament link group functionality to manage related filaments together
   -  Improved color coding system for inventory status with distinct purple shades for overstocked items
   -  Fixed issue where ideal quantities were reset after creating or deleting link groups

-  **Reliability Improvements**

   -  Implemented robust ideal quantity preservation system
   -  Added automatic detection and repair of zero ideal quantities
   -  Enhanced case-insensitive matching for filament records

-  **UI Enhancements**
   -  Improved visualization for filament groups with consistent color coding
   -  Better visual distinction between individual filaments and groups
   -  Enhanced status display with more consistent color indicators

### Version 1.1.0

-  **Bug Fixes**

   -  Fixed recursive call issue in print job search and filter functionality
   -  Improved signal handling to prevent UI freezes during filtering
   -  Enhanced error handling for database operations

-  **New Features**

   -  Added aggregated inventory view for better filament stock overview
   -  Improved component status tracking with visual indicators
   -  Enhanced reports with cost analysis capabilities
   -  Added data export functionality

-  **Performance Improvements**
   -  Optimized database queries for larger datasets
   -  Reduced memory usage for report generation
   -  Improved UI responsiveness

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/filament-consumption-tracker.git
cd filament-consumption-tracker
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python main.py
```

## Requirements

-  Python 3.7+
-  PyQt5 for the graphical interface
-  SQLAlchemy for database operations
-  Matplotlib for data visualization
-  Additional requirements specified in `requirements.txt`

## Database Location

The application stores its database in:

-  Windows: `%USERPROFILE%\Documents\FilamentTracker\filament_tracker.db`
-  Linux/Mac: `~/Documents/FilamentTracker/filament_tracker.db`

## Documentation

For detailed information about using and developing the application, please refer to:

-  [User Guide](docs/user_guide.md) - Comprehensive guide for using the application

   -  Basic usage instructions
   -  Feature-by-feature walkthrough
   -  Troubleshooting common issues
   -  Tips and best practices

-  [Developer Guide](docs/developer_guide.md) - Technical documentation for developers
   -  Architecture overview
   -  Database schema
   -  UI components
   -  Common issues and solutions
   -  Adding new features
   -  Testing procedures

## Screenshots

### Main Interface

[Screenshot of main interface with tabs]

### Filament Inventory

[Screenshot of filament inventory management]

### Print Job Tracking

[Screenshot of print job recording interface]

The Print Job Tracking interface allows users to record, manage, and analyze their 3D print jobs. Key features include:

-  **Recording new print jobs** with details on project name, printer used, filament(s), material quantity, and print duration
-  **Multicolor print support** with up to four different filaments per job
-  **Comprehensive history view** with sorting and filtering capabilities
-  **Template functionality** via right-click in job history:
   -  Right-click on any existing job to use it as a template for a new job
   -  All details including project name, printer, filament(s), quantities, and duration are copied
   -  Particularly useful when creating multiple similar print jobs or reprinting the same model with different filaments

### Reports and Analytics

[Screenshot of reports and charts]

## Known Issues

-  On some systems with high-DPI displays, UI scaling may need manual adjustment
-  Very large datasets (>10,000 print jobs) may cause performance slowdowns in reports
-  Date filtering in reports requires both start and end dates to be specified

## Creating a GitHub Repository

To create a GitHub repository for this project:

1. Login to your GitHub account
2. Click the "+" icon in the top-right corner and select "New repository"
3. Enter "Filament-Consumption-Tracker" as the repository name
4. Add a description: "A comprehensive application for tracking 3D printing filament usage and printer maintenance"
5. Choose "Public" repository
6. Select "Add a README file" (this file will be used)
7. Choose "Add .gitignore" and select "Python"
8. Select "Choose a license" and select "GNU General Public License v3.0"
9. Click "Create repository"

After creating the repository, push your local code:

```bash
# Initialize git repository (if not already initialized)
git init

# Add remote repository (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/Filament-Consumption-Tracker.git

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Push to GitHub
git push -u origin main
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](docs/developer_guide.md#contributing-guidelines) before submitting pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details. This license ensures that all modifications and derivative works will also remain open source.

## Acknowledgments

-  PyQt5 for the GUI framework
-  SQLAlchemy for database operations
-  Matplotlib for data visualization
-  The 3D printing community for inspiration and feedback

## Testing

The application includes a comprehensive test suite to verify functionality. To run all tests:

```
python run_tests.py
```

To run only the cost calculation tests:

```
python run_cost_tests.py
```

The test suite includes:

-  Database functionality tests
-  Schema model tests
-  UI component tests
-  Cost calculation tests
-  Cost analysis UI tests
