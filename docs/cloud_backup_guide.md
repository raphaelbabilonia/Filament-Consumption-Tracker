# Google Drive Cloud Backup & Sync Guide

This guide provides detailed information about using the Google Drive cloud backup and synchronization features in the Filament Consumption Tracker application.

## Overview

The cloud backup and sync features allow you to:

-  Back up your entire database to Google Drive
-  Restore from previous backups with a simple click
-  Automatically sync your database on a schedule (hourly, daily, or on exit)
-  Limit the number of backup files to save storage space
-  Securely store your data in the cloud
-  Access your data across multiple devices

## Setup

Before using the cloud features, you need to set up Google Drive API access. Please follow the detailed instructions in [google_drive_setup.md](./google_drive_setup.md).

## Using Cloud Backup

### Accessing the Cloud Backup Dialog

1. Start the Filament Consumption Tracker application
2. Go to the menu bar and select **File > Google Drive > Backup to Google Drive**
3. This will open the Google Drive Backup dialog

### Authentication

The first time you use the feature, you'll need to authenticate with Google:

1. In the Google Drive Backup dialog, click **Connect to Google Drive**
2. A browser window will open automatically
3. Sign in to your Google account if not already signed in
4. Grant the requested permissions to the application
5. Close the browser window when prompted
6. The application will show "Status: Connected to Google Drive" when successful

### Backing Up Your Database

#### Manual Backup

1. With the Google Drive Backup dialog open and authenticated
2. Click the **Backup to Drive** button
3. The backup process will begin, and you'll see a progress bar
4. When complete, you'll see a confirmation message
5. Your backup will be listed in the backup list

#### Automatic Backup on Exit

1. When closing the application, you'll be presented with options depending on your sync settings:
   -  If there are unsaved changes, you'll be asked if you want to save them
   -  If automatic sync is enabled for "On application close", you'll be asked if you want to sync
2. If you proceed with sync:
   -  A progress dialog will appear
   -  The backup will be performed
   -  The application will exit when the backup is complete
   -  You can cancel at any time

## New: Cloud Sync Settings

The application now includes advanced synchronization settings for better multi-device support:

### Accessing Sync Settings

1. Go to the menu bar and select **File > Google Drive > Sync Settings**
2. This will open the Sync Settings dialog

### Available Settings

1. **Enable Automatic Synchronization** - Turn automatic sync on/off
2. **Sync Frequency** - Choose when to perform automatic syncs:
   -  **On application close** - Sync each time you exit the application
   -  **Hourly** - Sync once per hour while the application is running
   -  **Daily** - Sync once per day while the application is running
3. **Maximum backups to keep** - Limit the number of backup files stored on Google Drive (1-50)
4. **Last sync** - Shows when your data was last synchronized

### Sync Now Button

-  The Sync Settings dialog includes a **Sync Now** button to trigger an immediate sync
-  This is useful to quickly sync your data without closing the application

### Unsaved Changes

-  If you have unsaved changes in any tab when automatic sync runs:
   -  The application will automatically save your changes first
   -  These changes will be part of the sync
   -  Modified items are indicated with bold text in tables

### Restoring from a Backup

1. Open the Google Drive Backup dialog
2. The list shows all available backups with timestamps
3. Select the backup you want to restore
4. Click the **Restore Selected Backup** button
5. Confirm the restoration when prompted
6. The application will download the backup and restore it
7. The application will restart with the restored database

## Multi-Device Workflow

To effectively use your data across multiple devices:

1. **Initial Setup**:
   -  Set up Google Drive on each device following the setup guide
   -  Create your initial database on one device
   -  Back up to Google Drive
2. **Subsequent Devices**:
   -  After setting up the application, restore from Google Drive
   -  Enable automatic sync with your preferred frequency
3. **Ongoing Workflow**:

   -  Each device will automatically sync changes based on your settings
   -  The maximum backup limit ensures you don't store unnecessary files
   -  Always check the "Last sync" timestamp to know when data was last synchronized

4. **Best Practices**:
   -  Use automatic sync "On application close" for devices used occasionally
   -  Use "Hourly" or "Daily" for devices used frequently or for extended periods
   -  Set a reasonable maximum backup limit (5-10 recommended)
   -  If you use multiple devices daily, manually sync important changes using the "Sync Now" button

## Performance Optimization

The backup system uses several optimizations to ensure fast and reliable backups:

### Smart Upload Strategy

-  **Small Databases** (<5MB): Uses direct upload for faster backups (5-15 seconds)
-  **Larger Databases**: Uses optimized chunked upload with 1MB chunks (15+ seconds)

### Reliability Features

-  **Automatic Cleanup**: Old backups beyond your specified limit are automatically removed
-  **Network Error Recovery**: Proper handling of connection issues
-  **Progress Tracking**: Real-time feedback during backup and restore

### UI Responsiveness

-  The application remains responsive during backup operations
-  Progress is displayed in real-time
-  Cancel option is always available

## Troubleshooting

### "Not Responding" Dialog

If Windows shows a "Not Responding" dialog briefly:

-  This can happen during authentication or when starting large uploads
-  The application should recover within a few seconds
-  Avoid clicking "End Process" as this will terminate the application

### Sync Not Running Automatically

If automatic sync isn't running:

-  Check if you're properly authenticated with Google Drive
-  Verify sync is enabled in the Sync Settings dialog
-  Check that the frequency setting matches your expectations
-  Look at the "Last sync" timestamp to see when the last sync occurred

### Authentication Issues

If authentication fails:

-  Ensure you've completed all steps in the setup guide
-  Check that the credentials.json file is in the correct location
-  Verify you've added yourself as a test user in Google Cloud Console

### Sync Conflicts

If you experience data conflicts when using multiple devices:

-  The system uses timestamps to determine the most recent backup
-  Ensure your system clocks are relatively synchronized across devices
-  When in doubt, perform a manual restore from the most up-to-date backup

## Security Considerations

-  The application uses OAuth 2.0 for secure authentication
-  Your Google password is never stored by the application
-  Only authentication tokens are stored locally
-  The app only has access to files it creates, not your entire Google Drive
-  All data is transferred securely over HTTPS
