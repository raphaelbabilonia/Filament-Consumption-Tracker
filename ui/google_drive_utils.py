"""
Utility module for Google Drive operations.
"""
import os
import pickle
import threading
import tempfile
import time
import socket
import ssl
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal, QMetaObject, Qt, Q_ARG, QTimer

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveAuthError(Exception):
    """Exception raised when authentication with Google Drive fails."""
    pass

class GoogleDriveHandler(QObject):
    """Handles Google Drive API operations."""
    
    # Define signals for async operations
    auth_completed = pyqtSignal(bool, str)
    upload_completed = pyqtSignal(bool, str, str)
    upload_progress = pyqtSignal(int)  # Progress percentage
    download_completed = pyqtSignal(bool, str, str)
    list_completed = pyqtSignal(bool, list, str)
    
    # Signal to start timer in main thread
    start_progress_timer = pyqtSignal()
    stop_progress_timer = pyqtSignal()
    
    def __init__(self, app_data_dir=None):
        """Initialize the Google Drive handler."""
        super().__init__()
        
        # Determine the application data directory
        if app_data_dir is None:
            self.app_data_dir = os.path.join(Path.home(), '.filament_tracker')
        else:
            self.app_data_dir = app_data_dir
            
        # Ensure the directory exists
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        # Path to store authentication token
        self.token_path = os.path.join(self.app_data_dir, 'token.pickle')
        self.credentials_path = os.path.join(self.app_data_dir, 'credentials.json')
        
        # Initialize service to None
        self.service = None
        
        # For upload cancellation
        self._upload_cancelled = False
        
        # Setup progress timer in main thread
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._emit_fake_progress)
        self._progress_current = 0
        
        # Connect signals for timer control
        self.start_progress_timer.connect(self._start_timer)
        self.stop_progress_timer.connect(self._stop_timer)
    
    def _start_timer(self):
        """Start the progress timer in the main thread."""
        self._progress_current = 0
        self._progress_timer.start(300)  # Update more frequently
        
    def _stop_timer(self):
        """Stop the progress timer in the main thread."""
        if self._progress_timer.isActive():
            self._progress_timer.stop()
            # Ensure we show 100% when completed
            self.upload_progress.emit(100)
    
    def authenticate(self, parent_widget=None, force_new=False):
        """
        Authenticate with Google Drive.
        
        Args:
            parent_widget: Parent widget for message boxes
            force_new: Force new authentication even if token exists
            
        Returns:
            True if authentication was successful
        """
        # If already authenticated and not forcing new auth, return immediately
        if self.is_authenticated() and not force_new:
            self.auth_completed.emit(True, "Already authenticated")
            return
            
        def auth_thread():
            try:
                creds = None
                
                # Remove existing token if force_new is True
                if force_new and os.path.exists(self.token_path):
                    os.remove(self.token_path)
                
                # Load existing token if it exists
                if os.path.exists(self.token_path):
                    with open(self.token_path, 'rb') as token:
                        creds = pickle.load(token)
                
                # Refresh token if expired
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    
                # If no valid credentials, get new ones
                if not creds or not creds.valid:
                    # Check if credentials.json exists
                    if not os.path.exists(self.credentials_path):
                        self.auth_completed.emit(False, "Missing credentials.json file")
                        return
                    
                    # This part needs to run in the main thread for the browser to open correctly
                    # Signal that we need to open a browser for authentication
                    QMetaObject.invokeMethod(
                        self, 
                        "_run_auth_flow", 
                        Qt.QueuedConnection,
                        Q_ARG(str, self.credentials_path)
                    )
                    return
                
                # Build the service
                self.service = build('drive', 'v3', credentials=creds)
                self.auth_completed.emit(True, "Authentication successful")
            
            except Exception as e:
                self.auth_completed.emit(False, str(e))
        
        # Start authentication in a separate thread
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def _run_auth_flow(self, credentials_path):
        """Run the OAuth flow in the main thread."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            
            # This will open a browser window for authentication
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            
            # Build the service
            self.service = build('drive', 'v3', credentials=creds)
            self.auth_completed.emit(True, "Authentication successful")
            
        except Exception as e:
            self.auth_completed.emit(False, str(e))
    
    def is_authenticated(self):
        """Check if already authenticated with Google Drive."""
        return self.service is not None
    
    def upload_file(self, file_path, file_name=None, folder_id=None):
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            file_name: Name to give the file in Google Drive (defaults to original name)
            folder_id: ID of the folder to upload to (None for root)
        """
        # Reset cancellation flag
        self._upload_cancelled = False
        
        # Store file_name in a variable that will be accessible in the thread
        _file_name = file_name if file_name is not None else os.path.basename(file_path)
        
        def upload_thread():
            try:
                if not self.is_authenticated():
                    self.upload_completed.emit(False, "", "Not authenticated with Google Drive")
                    return
                
                if not os.path.exists(file_path):
                    self.upload_completed.emit(False, "", f"File not found: {file_path}")
                    return
                
                # Get file size to determine upload strategy
                file_size = os.path.getsize(file_path)
                
                # Start progress updates (in main thread)
                self.start_progress_timer.emit()
                
                # Define file metadata
                file_metadata = {'name': _file_name}
                
                # Set parent folder if specified
                if folder_id:
                    file_metadata['parents'] = [folder_id]
                
                # Use simple upload for small files (faster)
                if file_size < 5 * 1024 * 1024:  # Less than 5 MB
                    try:
                        media = MediaFileUpload(file_path, resumable=False)
                        file = self.service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id'
                        ).execute()
                        
                        file_id = file.get('id')
                        self.stop_progress_timer.emit()
                        self.upload_completed.emit(True, file_id, f"File uploaded successfully with ID: {file_id}")
                        return
                    except Exception:
                        # If direct upload fails, fall back to chunked upload
                        pass
                
                # For larger files or if direct upload failed, use resumable upload
                # Create media object with optimized chunk size for better performance
                # Default chunk size is 256KB, we'll use a larger value for faster uploads
                chunk_size = 1024 * 1024 * 5  # 5 MB chunks
                media = MediaFileUpload(
                    file_path, 
                    resumable=True,
                    chunksize=chunk_size
                )
                
                # Create the upload request
                request = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                )
                
                # Maximum retry attempts for SSL errors
                max_retries = 3
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    try:
                        # Execute the request and handle response
                        response = None
                        while response is None:
                            if self._upload_cancelled:
                                self.stop_progress_timer.emit()
                                self.upload_completed.emit(False, "", "Upload cancelled by user")
                                return
                                
                            # This is a blocking call, but we simulate progress with our timer
                            # The actual API doesn't provide real-time progress
                            response = request.next_chunk()
                        
                        if response is not None:
                            # Upload completed successfully
                            file_id = response[1].get('id')
                            self.stop_progress_timer.emit()
                            self.upload_completed.emit(True, file_id, f"File uploaded successfully with ID: {file_id}")
                            success = True
                    
                    except (socket.error, ssl.SSLError) as e:
                        retry_count += 1
                        if retry_count >= max_retries:
                            # All retries failed
                            self.stop_progress_timer.emit()
                            self.upload_completed.emit(False, "", f"Upload failed after {max_retries} retries: {str(e)}")
                            return
                            
                        # Wait before retrying (shorter wait time)
                        time.sleep(1)
                        continue
                    
                    except Exception as e:
                        # Other errors - don't retry
                        self.stop_progress_timer.emit()
                        self.upload_completed.emit(False, "", f"Upload failed: {str(e)}")
                        return
                
            except Exception as e:
                self.stop_progress_timer.emit()
                self.upload_completed.emit(False, "", f"Upload failed: {str(e)}")
        
        # Start upload in a separate thread
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
    
    def _emit_fake_progress(self):
        """Emit fake progress to keep UI responsive during upload.
        Uses a non-linear curve to give impression of faster initial progress.
        """
        if self._progress_current < 95:
            # Non-linear progress simulation
            if self._progress_current < 30:
                # Start faster
                increment = 10
            elif self._progress_current < 60:
                # Medium speed
                increment = 5
            else:
                # Slow down near the end
                increment = 2
                
            self._progress_current += increment
            # Cap at 95% until we're actually done
            self._progress_current = min(95, self._progress_current)
            self.upload_progress.emit(self._progress_current)
    
    def cancel_upload(self):
        """Cancel the current upload operation."""
        self._upload_cancelled = True
        self.stop_progress_timer.emit()
        self.upload_completed.emit(False, "", "Upload cancelled by user")
    
    def download_file(self, file_id, destination_path):
        """
        Download a file from Google Drive.
        
        Args:
            file_id: ID of the file to download
            destination_path: Path where to save the downloaded file
        """
        def download_thread():
            try:
                if not self.is_authenticated():
                    self.download_completed.emit(False, "", "Not authenticated with Google Drive")
                    return
                
                # Create a temporary file for downloading
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Get the file from Drive
                request = self.service.files().get_media(fileId=file_id)
                
                with open(temp_path, 'wb') as f:
                    downloader = MediaIoBaseDownload(f, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                
                # Move the temp file to the destination
                os.replace(temp_path, destination_path)
                
                self.download_completed.emit(True, destination_path, "File downloaded successfully")
                
            except Exception as e:
                self.download_completed.emit(False, "", f"Download failed: {str(e)}")
                # Clean up temp file if it exists
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Start download in a separate thread (use daemon=True to not block application exit)
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def list_backup_files(self, name_filter=None):
        """
        List backup files in Google Drive.
        
        Args:
            name_filter: Optional filter for file name (e.g., '*.db')
        """
        def list_thread():
            try:
                if not self.is_authenticated():
                    self.list_completed.emit(False, [], "Not authenticated with Google Drive")
                    return
                
                # Build query string
                query = "trashed = false and mimeType != 'application/vnd.google-apps.folder'"
                
                if name_filter:
                    query += f" and name contains '{name_filter}'"
                
                # List files
                results = self.service.files().list(
                    q=query,
                    pageSize=50,
                    fields="files(id, name, createdTime, modifiedTime, size)"
                ).execute()
                
                files = results.get('files', [])
                self.list_completed.emit(True, files, "Files retrieved successfully")
                
            except Exception as e:
                self.list_completed.emit(False, [], f"Failed to list files: {str(e)}")
        
        # Start listing in a separate thread (use daemon=True to not block application exit)
        thread = threading.Thread(target=list_thread, daemon=True)
        thread.start()
    
    def create_or_get_app_folder(self, folder_name="Filament Tracker Backups"):
        """
        Create or get the application folder in Google Drive.
        
        Args:
            folder_name: Name of the application folder
            
        Returns:
            The folder ID or None if failed
        """
        try:
            if not self.is_authenticated():
                return None
            
            # Check if folder already exists
            query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            items = results.get('files', [])
            
            # If folder exists, return its ID
            if items:
                return items[0]['id']
            
            # Create folder if it doesn't exist
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')
            
        except Exception:
            return None 