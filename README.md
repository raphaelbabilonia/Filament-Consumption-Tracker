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

-  **Data Management**
   -  Built-in backup and restore functionality
   -  Data export to CSV format
   -  Automatic database versioning

## Recent Updates

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
