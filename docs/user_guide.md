# Filament Consumption Tracker - User Guide

Welcome to the Filament Consumption Tracker! This guide will help you understand how to use all the features of the application effectively.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Managing Filaments](#managing-filaments)
3. [Tracking Print Jobs](#tracking-print-jobs)
4. [Printer Management](#printer-management)
5. [Reports and Analytics](#reports-and-analytics)
6. [Tips and Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Data Management](#data-management)

## Getting Started

### First Launch
When you first launch the application, you'll see four main tabs:
- Print Jobs
- Filament Inventory
- Printer Management
- Reports

### Initial Setup
1. Start by adding your printers in the Printer Management tab
2. Add your filament inventory in the Filament Inventory tab
3. You can then begin tracking print jobs

## Managing Filaments

### Adding New Filament
1. Go to the "Filament Inventory" tab
2. Fill in the required information:
   - Type (PLA, ABS, PETG, etc.)
   - Color
   - Brand
   - Spool Weight (in grams)
   - Remaining Quantity (defaults to spool weight for new spools)
   - Price (optional)
   - Purchase Date
3. Click "Add Filament"

### Monitoring Inventory
- The table shows all your filament spools with remaining quantities
- Low stock items (< 20% remaining) are highlighted in red
- You can edit quantities by selecting a filament and clicking "Edit Selected"
- The "Aggregated Inventory" tab shows total filament by type/color/brand combinations

### Removing Filament
1. Select the filament in the table
2. Click "Delete Selected"
3. Confirm the deletion
Note: Filaments used in print jobs cannot be deleted

## Tracking Print Jobs

### Recording a Print Job
1. Go to the "Print Jobs" tab
2. Enter the project name
3. Select the filament used
4. Select the printer used
5. Enter the amount of filament used (in grams)
6. Enter the print duration (in hours)
7. Add any notes (optional)
8. Click "Add Print Job"

### Viewing Print History
- All print jobs are displayed in the table below the entry form
- You can filter jobs by:
  - Using the search box to find projects, filaments, or printers
  - Using dropdown filters for specific printers or filament types
- You can refresh filament data using the "Refresh Filament Data" button

### Exporting Data
1. Use filters to select the data you want to export
2. Click "Export Jobs to CSV"
3. Choose a location to save the CSV file
4. All visible jobs will be included in the export

## Printer Management

### Adding a Printer
1. Go to the "Printer Management" tab
2. Enter the printer name
3. Enter the model (optional)
4. Add any notes (optional)
5. Click "Add Printer"

### Managing Components
1. Select a printer
2. Click "Add Component"
3. Enter component details:
   - Name
   - Replacement Interval (in hours)
   - Notes (optional)
4. The system will track component usage based on print times

### Maintenance Tracking
- Components due for replacement are highlighted in red
- You can reset component hours after replacement
- The system provides warnings when components near their replacement interval

## Reports and Analytics

### Usage Summary
- Shows filament consumption over time
- Can be grouped by:
  - Filament Type
  - Filament Color
  - Filament Brand
  - Printer
  - Cost Analysis
- Set date ranges to analyze specific time periods

### Inventory Status
- Current inventory levels
- Low stock warnings 
- Views available:
  - By Type (pie chart)
  - By Color (pie chart)
  - By Brand (pie chart)
  - Low Stock Items (bar chart with items under 20% remaining)

### Printer Statistics
- Print hours by printer
- Material usage by printer
- Job counts by printer
- Filter by time period:
  - All Time
  - This Month
  - This Year

### Component Status
- Maintenance schedules
- Component life tracking
- Replacement predictions with color indicators:
  - Green: OK
  - Orange: Replace Soon (>80% of replacement interval)
  - Red: Replace Now (>=100% of replacement interval)

## Tips and Best Practices

### Accurate Tracking
1. Always weigh spools before and after large prints
2. Update remaining quantities regularly
3. Note any issues or quality variations in print job notes

### Inventory Management
1. Set up low stock alerts (20% by default)
2. Keep track of purchase dates and costs
3. Note any storage requirements in filament notes

### Maintenance
1. Regularly check component status
2. Reset component hours after replacement
3. Keep detailed notes of maintenance activities

## Troubleshooting

### Common Issues

#### Search and Filter Issues
- If searching or filtering seems to cause freezing or errors:
  - Clear the search box first
  - Apply filters one at a time
  - If issues persist, use the "Refresh" option from the File menu

#### Missing Data
- Ensure all required fields are filled when adding entries
- Check for proper number formats (no letters in number fields)
- Try refreshing the data using the "Refresh Data" option in the File menu

#### Calculation Errors
- Verify spool weights and remaining quantities
- Ensure print job filament usage doesn't exceed available quantity
- Check for negative values in quantity fields

#### UI Issues
- If the application becomes unresponsive when searching or filtering:
  - Clear the search box
  - Restart the application if issues persist
- If tabs don't update properly when switching between them:
  - Use the "Refresh Data" option in the File menu

### Getting Help
If you encounter issues not covered in this guide:
1. Check the error message for specific information
2. Consult the developer guide for technical details
3. Report issues through the project's issue tracker

## Data Management

### Backup and Restore
The application provides built-in backup and restore functionality:
1. Go to File → Backup Database to save a copy of your data
2. Go to File → Restore Database to recover from a backup
3. Backups are date-stamped for easy identification

### Regular Backups
- We recommend creating backups before:
  - Making significant changes to your inventory
  - Deleting multiple records
  - Updating to a new version of the application

### Database Location
The application stores its database at:
- Default location: In the application directory
- You can specify a custom location in the settings

## Keyboard Shortcuts
- F5: Refresh all data
- Ctrl+Q: Exit application
- Tab: Navigate between fields
- Enter: Submit forms

## Recent Updates
- Fixed search and filter functionality to prevent application freezing
- Improved inventory tracking with aggregated view
- Added cost analysis reporting
- Enhanced printer component tracking with status indicators
- Added data backup and restore capabilities