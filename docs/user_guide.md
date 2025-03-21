# Filament Consumption Tracker - User Guide

Welcome to the Filament Consumption Tracker! This guide will help you understand how to use all the features of the application effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Managing Filaments](#managing-filaments)
3. [Filament Link Groups](#filament-link-groups)
4. [Ideal Quantities](#ideal-quantities)
5. [Tracking Print Jobs](#tracking-print-jobs)
6. [Printer Management](#printer-management)
7. [Reports and Analytics](#reports-and-analytics)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)
10.   [Data Management](#data-management)

## Getting Started

### First Launch

When you first launch the application, you'll see four main tabs:

-  Print Jobs
-  Filament Inventory
-  Printer Management
-  Reports

### Initial Setup

1. Start by adding your printers in the Printer Management tab
2. Add your filament inventory in the Filament Inventory tab
3. You can then begin tracking print jobs

## Managing Filaments

### Adding New Filament

1. Go to the "Filament Inventory" tab
2. Fill in the required information:
   -  Type (PLA, ABS, PETG, etc.)
   -  Color
   -  Brand
   -  Spool Weight (in grams)
   -  Remaining Quantity (defaults to spool weight for new spools)
   -  Price (optional)
   -  Purchase Date
3. Click "Add Filament"

### Monitoring Inventory

-  The table shows all your filament spools with remaining quantities
-  Low stock items (< 20% remaining) are highlighted in red
-  You can edit quantities by selecting a filament and clicking "Edit Selected"
-  The "Aggregated Inventory" tab shows total filament by type/color/brand combinations

### Removing Filament

1. Select the filament in the table
2. Click "Delete Selected"
3. Confirm the deletion
   Note: Filaments used in print jobs cannot be deleted

## Filament Link Groups

### What Are Filament Link Groups?

Filament Link Groups allow you to combine related filaments that serve a similar purpose or are interchangeable. This helps you manage inventory more effectively by:

-  Setting a single ideal quantity target for a group of filaments
-  Viewing combined inventory levels for related materials
-  Managing multiple filaments as a single entity

### Creating a Link Group

1. Go to the "Inventory Status" tab under "Filament Inventory"
2. Click the "Manage Link Groups" button
3. Select "Create New Link Group" from the menu
4. Enter the group details:
   -  Name: A descriptive name for the group (e.g., "White PLA Variants")
   -  Description: Optional information about the group
   -  Ideal Quantity: The target inventory level for this group in grams

### Adding Filaments to a Group

1. Open the Link Group by clicking "Edit" next to the group name
2. Click "Add Filament"
3. Select filaments from the list (you can search/filter to find specific filaments)
4. Check the box next to each filament you want to add
5. Click "Add Selected"

### Removing Filaments from a Group

1. Open the Link Group by clicking "Edit" next to the group name
2. Select the filament in the group list
3. Click "Remove Selected"
4. Confirm the removal

### Deleting a Link Group

1. Click the "Manage Link Groups" button
2. Select "Delete" next to the group you want to remove
3. Confirm the deletion
   Note: Deleting a group does not delete the filaments within it

## Ideal Quantities

### Setting Ideal Quantities

Ideal quantities help you maintain optimal inventory levels for each filament type or group.

1. In the "Inventory Status" tab, select a filament
2. Click the "Set Ideal Quantity" button
3. Enter the target quantity in grams
4. Click "Save"

### Inventory Status Indicators

The system uses color-coding to indicate inventory status based on ideal quantities:

-  **No Target Set (Light Gray)**: No ideal quantity has been set
-  **Out of Stock (Very Light Red)**: 0% of ideal quantity
-  **Critical - Order Now (Very Light Red)**: Less than 20% of ideal quantity
-  **Low - Order Soon (Very Light Orange)**: Between 20% and 50% of ideal quantity
-  **Adequate (Very Light Yellow)**: Between 50% and 95% of ideal quantity
-  **Optimal (Very Light Green)**: Between 95% and 120% of ideal quantity
-  **Overstocked (Very Light Purple)**: More than 120% of ideal quantity

### Group Quantities

For filament groups, the status is calculated based on:

-  Combined current quantity of all filaments in the group
-  The ideal quantity set for the entire group

### Preservation of Ideal Quantities

The system now preserves ideal quantities automatically when:

-  Creating new link groups
-  Deleting existing link groups
-  Adding filaments to groups
-  Removing filaments from groups

## Tracking Print Jobs

### Recording a Print Job

1. Go to the "Print Jobs" tab
2. Enter the project name
3. Select the printer used
4. Select the primary filament used
   -  Each filament displays its ID for easy identification of spools
   -  The ID is visible next to the filament name (e.g., "Brand Color Type - ID:X")
5. Enter the amount of filament used (in grams)
6. For multicolor prints:
   -  Check the "Multicolor Print" checkbox
   -  Select the number of additional filaments (1-3) from the spinner
   -  Select each additional filament and enter the amount used
7. Enter the print duration:
   -  Specify hours and minutes separately in the respective fields
   -  For example, 2h 30m for a two and a half hour print
8. Enter the date and time (defaults to current time)
9. Add any notes (optional)
10.   Click "Add Print Job"

### Working with Multicolor Prints

The multicolor feature enables tracking of up to 3 additional filaments per print job:

1. Check the "Multicolor Print" checkbox to enable secondary filament selection
2. Use the "Number of additional filaments" spinner to specify how many additional filaments you used (1-3)
3. The interface will dynamically show only the needed number of filament selectors
4. Each filament selector displays the filament ID for easy spool identification
5. Enter the amount of each additional filament used

### Viewing Print History

-  All print jobs are displayed in the table below the entry form
-  The date column displays dates in dd/mm/yy format for easy reading
-  You can sort the table by clicking on any column header
-  Use the search and filter controls to find specific jobs
-  Total costs are calculated and displayed based on material cost and electricity usage

### Using Existing Jobs as Templates

The application allows you to use existing print jobs as templates for new ones:

1. In the print job history table, right-click on any job you want to use as a template
2. Select "Use as template for new job" from the context menu
3. The "Record New Print Job" form will be populated with all details from the selected job:
   -  Project name
   -  Printer selection
   -  Primary and additional filaments (if multicolor)
   -  Amount of filament(s) used
   -  Print duration
   -  Notes
4. Review and modify any details as needed
5. Click "Add Print Job" to create a new job based on this template

This feature is particularly useful when:

-  Creating similar print jobs with minor modifications
-  Recording multiple prints of the same model
-  Testing different settings with the same model
-  Using the same project with different filament colors

### Exporting Data

1. Use filters to select the data you want to export
2. Click "Export to CSV"
3. Choose a location to save the file
4. The exported CSV will include all job details including dates, materials, printer, and costs
5. Cost data is included without currency symbols for easy spreadsheet analysis

## Printer Management

### Adding a Printer

1. Go to the "Printer Management" tab
2. Enter the printer name
3. Enter the model (optional)
4. Enter the power consumption in kWh (optional but recommended for electricity cost calculations)
5. Add any notes (optional)
6. Click "Add Printer"

### Setting Electricity Cost

1. Go to the "Printer Management" tab
2. Click the "Set Electricity Cost" button
3. Enter your electricity cost per kWh
4. Click "OK" to save
5. This global setting will be used for all electricity cost calculations throughout the application

### Managing Components

1. Select a printer
2. Click "Add Component"
3. Enter component details:
   -  Name
   -  Replacement Interval (in hours)
   -  Notes (optional)
4. The system will track component usage based on print times

### Editing Components

1. Go to the "Components" tab in the Printer Management section
2. Select the component you want to modify
3. Click "Edit Component"
4. You can edit the following information:
   -  Component Name
   -  Replacement Interval (in hours)
   -  Installation Date
   -  Usage Hours
   -  Notes
5. Click "Save Changes" to update the component information

### Maintenance Tracking

-  Components due for replacement are highlighted in red
-  You can reset component hours after replacement
-  The system provides warnings when components near their replacement interval

## Reports and Analytics

### Usage Summary

-  Shows filament consumption over time
-  Can be grouped by:
   -  Filament Type
   -  Filament Color
   -  Filament Brand
   -  Printer
   -  Cost Analysis
-  Set date ranges to analyze specific time periods

### Inventory Status

-  Current inventory levels
-  Low stock warnings
-  Views available:
   -  By Type (pie chart)
   -  By Color (pie chart)
   -  By Brand (pie chart)
   -  Low Stock Items (bar chart with items under 20% remaining)

### Printer Statistics

-  Print hours by printer
-  Material usage by printer
-  Job counts by printer
-  Electricity costs based on power consumption and print duration
-  Filter by time period:
   -  All Time
   -  This Month
   -  This Year
-  Temporarily adjust electricity cost per kWh for what-if scenarios (without changing the global setting)

### Cost Analysis

-  Complete breakdown of printing costs
-  Material costs based on filament prices
-  Electricity costs based on printer power consumption
-  Visual comparison charts:
   -  Pie chart showing cost distribution (material vs. electricity)
   -  Bar chart comparing costs by project, filament type, or printer
-  Detailed cost table with totals
-  Group data by:
   -  Project
   -  Filament Type
   -  Printer
-  Filter by time period with the same options as other reports
-  Temporarily adjust electricity cost per kWh for what-if scenarios (without changing the global setting)

### Component Status

-  Maintenance schedules
-  Component life tracking
-  Replacement predictions with color indicators:
   -  Green: OK
   -  Orange: Replace Soon (>80% of replacement interval)
   -  Red: Replace Now (>=100% of replacement interval)

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

-  If searching or filtering seems to cause freezing or errors:
   -  Clear the search box first
   -  Apply filters one at a time
   -  If issues persist, use the "Refresh" option from the File menu

#### Missing Data

-  Ensure all required fields are filled when adding entries
-  Check for proper number formats (no letters in number fields)
-  Try refreshing the data using the "Refresh Data" option in the File menu

#### Calculation Errors

-  Verify spool weights and remaining quantities
-  Ensure print job filament usage doesn't exceed available quantity
-  Check for negative values in quantity fields

#### UI Issues

-  If the application becomes unresponsive when searching or filtering:
   -  Clear the search box
   -  Restart the application if issues persist
-  If tabs don't update properly when switching between them:
   -  Use the "Refresh Data" option in the File menu

### Getting Help

If you encounter issues not covered in this guide:

1. Check the error message for specific information
2. Consult the developer guide for technical details
3. Report issues through the project's issue tracker

## Data Management

### Local Backup and Restore

1. Go to **File > Backup Database**
2. Choose a location to save your backup file
3. The file will be saved with a timestamp in the filename

To restore:

1. Go to **File > Restore Database**
2. Browse to your backup file
3. Confirm the restoration

### Google Drive Backup

For detailed instructions on setting up and using Google Drive for backup, see [cloud_backup_guide.md](./cloud_backup_guide.md).

Basic steps:

1. Set up Google Drive access using instructions in [google_drive_setup.md](./google_drive_setup.md)
2. Go to **File > Google Drive > Backup to Google Drive**
3. Follow the prompts to authenticate and complete the backup

### New: Cloud Sync and Multi-Device Support

The Filament Consumption Tracker now includes powerful cloud synchronization features that let you keep your data synchronized across multiple devices. This is ideal if you:

-  Use the application on both a desktop and laptop computer
-  Have a shared workshop where multiple people track filament usage
-  Want automatic backups without manual intervention

#### Setting Up Cloud Sync

1. Go to **File > Google Drive > Sync Settings**
2. In the Sync Settings dialog:
   -  Check **Enable automatic synchronization** to turn on the feature
   -  Select your preferred frequency:
      -  **On application close** - Sync each time you exit the app
      -  **Hourly** - Sync automatically once every hour
      -  **Daily** - Sync once per day
   -  Set the **Maximum backups to keep** (recommended: 5-10)
3. Click **OK** to save your settings

#### Using Cloud Sync

Once enabled, the synchronization happens automatically based on your settings. You can also:

-  Click **Sync Now** in the Sync Settings dialog to perform an immediate sync
-  See when your data was last synchronized in the **Last sync** field
-  Check for unsaved changes in the tables (modified items appear in **bold**)

#### Multi-Device Workflow

To use the application on multiple devices:

1. **First Device Setup**:
   -  Set up the application normally
   -  Configure Google Drive access
   -  Create your database and enable automatic sync
2. **Additional Devices**:
   -  Install the application
   -  Configure Google Drive access
   -  Instead of creating a new database, restore from your Google Drive backup
   -  Enable automatic sync with your preferred settings
3. **Daily Usage**:
   -  Make changes on any device
   -  The changes will automatically sync based on your settings
   -  Always check the "Last sync" timestamp to know how current your data is
   -  Use "Sync Now" when you need immediate synchronization

#### Recommendations

-  For a desktop computer that's always on, use **Hourly** sync
-  For laptops or less frequently used devices, use **On application close**
-  Set a reasonable backup limit (5-10) to avoid using too much storage
-  After making important changes, use **Sync Now** to ensure they're immediately backed up
-  When restoring on a new device, always choose the most recent backup file

#### Troubleshooting

If synchronization isn't working:

1. Check your internet connection
2. Verify you're properly authenticated with Google Drive
3. Check if automatic sync is enabled in settings
4. Use "Sync Now" to manually trigger a sync and check for error messages
5. Look at the "Last sync" timestamp to see if sync is actually running
6. For persistent issues, try restoring from a known good backup

## Keyboard Shortcuts

-  F5: Refresh all data
-  Ctrl+Q: Exit application
-  Tab: Navigate between fields
-  Enter: Submit forms

## Recent Updates

-  Added global electricity cost per kWh setting in Printer Management tab
-  Implemented comprehensive cost calculation for print jobs (material and electricity)
-  Added new Cost Analysis tab with detailed cost breakdowns and visualizations
-  Enhanced Printer Usage tab with electricity cost reporting
-  Fixed search and filter functionality to prevent application freezing
-  Improved inventory tracking with aggregated view
-  Enhanced printer component tracking with status indicators
-  Added data backup and restore capabilities
