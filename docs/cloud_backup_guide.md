# Google Drive Cloud Backup Guide

This guide provides detailed information about using the Google Drive cloud backup feature in the Filament Consumption Tracker application.

## Overview

The cloud backup feature allows you to:

-  Back up your entire database to Google Drive
-  Restore from previous backups with a simple click
-  Automatically back up when exiting the application
-  Securely store your data in the cloud

## Setup

Before using the cloud backup feature, you need to set up Google Drive API access. Please follow the detailed instructions in [google_drive_setup.md](./google_drive_setup.md).

## Using Cloud Backup

### Accessing the Cloud Backup Dialog

1. Start the Filament Consumption Tracker application
2. Go to the menu bar and select **File > Cloud Backup > Google Drive Backup**
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

1. When closing the application, you'll be presented with three options:
   -  **Cancel** - Cancel the exit operation
   -  **Exit** - Exit without backing up
   -  **Backup and Exit** - Backup your database to Google Drive and then exit
2. If you select "Backup and Exit":
   -  A progress dialog will appear
   -  The backup will be performed
   -  The application will exit when the backup is complete
   -  You can cancel at any time

### Restoring from a Backup

1. Open the Google Drive Backup dialog
2. The list shows all available backups with timestamps
3. Select the backup you want to restore
4. Click the **Restore Selected Backup** button
5. Confirm the restoration when prompted
6. The application will download the backup and restore it
7. The application will restart with the restored database

## Performance Optimization

The backup system uses several optimizations to ensure fast and reliable backups:

### Smart Upload Strategy

-  **Small Databases** (<5MB): Uses direct upload for faster backups (5-15 seconds)
-  **Larger Databases**: Uses optimized chunked upload with 5MB chunks (15+ seconds)

### Reliability Features

-  **SSL Error Handling**: Automatically retries up to 3 times with exponential backoff
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

### SSL Errors

If you see SSL errors like "MIXED_HANDSHAKE_AND_NON_HANDSHAKE_DATA":

-  These are typically temporary network issues
-  The application will automatically retry (up to 3 times)
-  If persistent, check your internet connection and try again later

### Authentication Issues

If authentication fails:

-  Ensure you've completed all steps in the setup guide
-  Check that the credentials.json file is in the correct location
-  Verify you've added yourself as a test user in Google Cloud Console

### Slow Uploads

If uploads are taking too long:

-  Check your internet connection speed, especially upload bandwidth
-  Larger databases will naturally take longer to upload
-  Consider using local backup for very large databases

## Security Considerations

-  The application uses OAuth 2.0 for secure authentication
-  Your Google password is never stored by the application
-  Only authentication tokens are stored locally
-  The app only has access to files it creates, not your entire Google Drive
-  All data is transferred securely over HTTPS
