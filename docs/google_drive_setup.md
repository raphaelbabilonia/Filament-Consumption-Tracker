# Setting up Google Drive Backup

This guide explains how to set up cloud backup using Google Drive for your Filament Consumption Tracker application.

## Features

-  **Automated cloud backup** of your database to Google Drive
-  **Secure OAuth 2.0 authentication** - no password storage
-  **Fast direct upload** for small databases
-  **Chunked uploads** for larger databases with automatic retry
-  **Backup on exit option** for seamless workflow
-  **Easy restoration** from any saved backup

## Prerequisites

-  A Google account
-  Internet connection
-  Filament Consumption Tracker application with Google Drive backup feature

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name your project (e.g., "Filament Tracker Backup")
4. Click "Create"

## Step 2: Enable the Google Drive API

1. In your Google Cloud project, go to the Navigation menu and select "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API" in the results
4. Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" as the user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   -  App name: "Filament Consumption Tracker"
   -  User support email: Your email address
   -  Developer contact information: Your email address
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add the scope: `https://www.googleapis.com/auth/drive.file`
8. Click "Save and Continue"
9. Add test users (your Google email) on the "Test users" page
10.   Click "Save and Continue"
11.   Review your settings and click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Name your OAuth client (e.g., "Filament Tracker Desktop Client")
5. Click "Create"
6. Click "Download JSON" to download your credentials file
7. Rename the downloaded file to `credentials.json`

## Step 5: Add Credentials to Your Application

1. Locate your Filament Consumption Tracker application data directory:

   -  Windows: `C:\Users\<YourUsername>\.filament_tracker`
   -  macOS: `/Users/<YourUsername>/.filament_tracker`
   -  Linux: `/home/<YourUsername>/.filament_tracker`

2. If the directory doesn't exist, create it
3. Place the `credentials.json` file in this directory

## Using Google Drive Backup

### Manual Backup

1. Open the Filament Consumption Tracker application
2. Go to File > Cloud Backup > Google Drive Backup
3. When prompted, click "Connect to Google Drive"
4. Your browser will open and ask you to sign in to your Google account
5. Grant the requested permissions to the application
6. After successful authentication, click "Backup to Drive"
7. Wait for the backup to complete - a success message will appear when done

### Backup on Exit

The application also offers an option to back up when exiting:

1. When closing the application, you'll be prompted with three options:
   -  "Cancel" - Cancel the exit
   -  "Exit" - Exit without backup
   -  "Backup and Exit" - Backup to Google Drive and then exit
2. If you select "Backup and Exit":
   -  A progress dialog will show the backup status
   -  You can cancel the backup if needed
   -  Once complete, the application will exit

### Restoring from Backup

1. Go to File > Cloud Backup > Google Drive Backup
2. When the dialog opens, you'll see a list of available backups on Google Drive
3. Select the backup you want to restore from the list
4. Click "Restore Selected Backup"
5. Confirm the restoration when prompted
6. Wait for the download to complete - your database will be restored automatically

## Performance Considerations

-  **Small Databases** (<5MB): Uses direct upload for faster backups
-  **Larger Databases**: Uses chunked uploads with optimized 5MB chunks
-  **Network Issues**: Automatically retries up to 3 times with SSL errors
-  **Upload Speed**: Depends on your internet connection (especially upload bandwidth)
-  **Typical Backup Times**:
   -  Small DB (<5MB): ~5-15 seconds
   -  Medium DB (5-20MB): ~15-45 seconds
   -  Large DB (>20MB): 1+ minutes depending on size

## Troubleshooting

-  **"Missing credentials.json file" error**: Make sure you've placed the credentials.json file in the correct location.
-  **Authentication fails**: Ensure you've enabled the Google Drive API and configured the OAuth consent screen correctly.
-  **Permission denied**: Make sure you've added yourself as a test user in the OAuth consent screen.
-  **SSL Errors**: These are usually temporary network issues. Try again later or check your internet connection.
-  **Slow uploads**: Check your internet connection speed, especially upload bandwidth.
-  **"Not Responding" dialog**: The application may briefly show this during authentication or when starting uploads, but should recover within a few seconds.

## Security Note

The application only requests access to files it creates (using the `drive.file` scope), not your entire Google Drive. Your Google credentials are never stored by the application - it uses OAuth 2.0 tokens instead, which are securely stored in your user directory.
