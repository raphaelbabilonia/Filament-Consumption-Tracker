"""
Dialog for Google Drive backup operations.
"""
import os
import datetime
import shutil
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QListWidget, QProgressBar,
                            QMessageBox, QFileDialog, QAbstractItemView,
                            QDialogButtonBox, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from ui.google_drive_utils import GoogleDriveHandler

class DriveBackupDialog(QDialog):
    """Dialog for Google Drive backup and restore operations."""
    
    def __init__(self, parent=None, db_handler=None):
        """Initialize the Google Drive backup dialog."""
        super().__init__(parent)
        
        self.parent = parent
        self.db_handler = db_handler
        self.drive_handler = GoogleDriveHandler()
        self.app_folder_id = None
        
        # Setup UI
        self.setWindowTitle("Google Drive Backup")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Authenticate on startup
        self.authenticate()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Status section
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Not connected to Google Drive")
        status_layout.addWidget(self.status_label)
        
        self.auth_button = QPushButton("Connect to Google Drive")
        status_layout.addWidget(self.auth_button)
        
        layout.addLayout(status_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Files list section
        list_label = QLabel("Available backups on Google Drive:")
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.file_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh List")
        self.backup_button = QPushButton("Backup to Drive")
        self.restore_button = QPushButton("Restore Selected Backup")
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.backup_button)
        button_layout.addWidget(self.restore_button)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
        
        # Initially disable buttons until authenticated
        self.set_controls_enabled(False)
        
    def connect_signals(self):
        """Connect signals to slots."""
        # Button connections
        self.auth_button.clicked.connect(self.authenticate)
        self.refresh_button.clicked.connect(self.refresh_file_list)
        self.backup_button.clicked.connect(self.backup_to_drive)
        self.restore_button.clicked.connect(self.restore_from_drive)
        self.button_box.rejected.connect(self.reject)
        
        # Google Drive handler signals
        self.drive_handler.auth_completed.connect(self.on_auth_completed)
        self.drive_handler.upload_completed.connect(self.on_upload_completed)
        self.drive_handler.download_completed.connect(self.on_download_completed)
        self.drive_handler.list_completed.connect(self.on_list_completed)
        self.drive_handler.upload_progress.connect(self.on_upload_progress)
        
    def authenticate(self, force_new=False):
        """Authenticate with Google Drive."""
        # Check if already authenticated
        if self.drive_handler.is_authenticated() and not force_new:
            # Already authenticated, emit success signal directly
            self.drive_handler.auth_completed.emit(True, "Already authenticated")
            return
            
        self.status_label.setText("Status: Connecting to Google Drive...")
        self.auth_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start authentication
        self.drive_handler.authenticate(self, force_new)
        
    def on_auth_completed(self, success, message):
        """Handle authentication completion."""
        if success:
            self.status_label.setText("Status: Connected to Google Drive")
            self.auth_button.setText("Re-authenticate")
            self.auth_button.setEnabled(True)
            
            # Get or create the app folder
            self.app_folder_id = self.drive_handler.create_or_get_app_folder()
            
            # Enable controls
            self.set_controls_enabled(True)
            
            # Load files
            self.refresh_file_list()
        else:
            self.status_label.setText(f"Status: Authentication failed - {message}")
            self.auth_button.setText("Retry Connection")
            self.auth_button.setEnabled(True)
            
            # Show error if credentials are missing
            if "Missing credentials.json" in message:
                QMessageBox.critical(
                    self,
                    "Missing Credentials",
                    "Google API credentials file (credentials.json) is missing.\n\n"
                    "Please obtain credentials from Google Cloud Console and save them to:\n"
                    f"{self.drive_handler.credentials_path}"
                )
        
        self.progress_bar.setVisible(False)
        
    def refresh_file_list(self):
        """Refresh the list of backup files from Google Drive."""
        self.status_label.setText("Status: Retrieving backup files...")
        self.progress_bar.setVisible(True)
        self.set_controls_enabled(False)
        
        # Clear the list
        self.file_list.clear()
        
        # Get the list of backup files
        self.drive_handler.list_backup_files("filament_tracker_backup")
        
    def on_list_completed(self, success, files, message):
        """Handle file list completion."""
        if success:
            self.status_label.setText("Status: Connected to Google Drive")
            
            # Add files to the list
            for file in files:
                item = QListWidgetItem(file['name'])
                item.setData(Qt.UserRole, file)
                
                # Format created time
                if 'createdTime' in file:
                    created_time = file['createdTime']
                    # Convert from ISO format
                    try:
                        dt = datetime.datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                        item.setToolTip(f"Created: {formatted_time}")
                    except:
                        item.setToolTip(f"Created: {created_time}")
                
                self.file_list.addItem(item)
                
            if not files:
                self.status_label.setText("Status: No backup files found on Google Drive")
        else:
            self.status_label.setText(f"Status: Failed to retrieve files - {message}")
            
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)
        self.restore_button.setEnabled(self.file_list.count() > 0)
        
    def backup_to_drive(self):
        """Backup the database to Google Drive."""
        if not self.drive_handler.is_authenticated():
            QMessageBox.warning(
                self,
                "Authentication Required",
                "Please authenticate with Google Drive first."
            )
            return
        
        # Set up UI for backup operation
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing backup...")
        self.set_controls_enabled(False)
        
        # Create backup file name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"filament_tracker_backup_{timestamp}.db"
        
        # Determine where to store the backup file
        temp_dir = os.path.dirname(self.db_handler.db_path)
        backup_path = os.path.join(temp_dir, backup_filename)
        
        try:
            # Copy the database file to the backup location
            shutil.copy2(self.db_handler.db_path, backup_path)
            
            # Get max backups setting
            max_backups = 5  # Default
            try:
                settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'database', 'sync_settings.json')
                if os.path.exists(settings_path):
                    with open(settings_path, 'r') as f:
                        settings = json.load(f)
                        max_backups = settings.get("max_backups", 5)
            except Exception:
                pass
                
            # Upload to Google Drive
            self.status_label.setText("Uploading to Google Drive...")
            self.drive_handler.upload_file(
                backup_path, 
                backup_filename, 
                self.app_folder_id,
                max_backups=max_backups
            )
            
        except Exception as e:
            self.set_controls_enabled(True)
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Failed to create backup file: {str(e)}"
            )
            
            # Clean up
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except:
                    pass
    
    def on_upload_completed(self, success, file_id, message):
        """Handle upload completion."""
        if success:
            self.status_label.setText("Status: Backup completed successfully")
            QMessageBox.information(
                self,
                "Backup Complete",
                "Database successfully backed up to Google Drive."
            )
            # Refresh the file list
            self.refresh_file_list()
        else:
            self.status_label.setText(f"Status: Backup failed - {message}")
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Failed to backup database: {message}"
            )
            
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)
        
    def restore_from_drive(self):
        """Restore database from Google Drive."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a backup file to restore."
            )
            return
            
        # Get the selected file information
        selected_item = selected_items[0]
        file_info = selected_item.data(Qt.UserRole)
        
        # Confirm restoration
        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            f"Restoring from '{file_info['name']}' will overwrite all current data. "
            "This action cannot be undone.\n\n"
            "Are you sure you want to restore from this backup?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            # Get the current database path
            db_path = self.db_handler.engine.url.database
            
            # Create a backup of the current database just in case
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"{db_path}.{timestamp}.bak"
            
            # Create a copy of the current database
            import shutil
            shutil.copy2(db_path, current_backup)
            
            # Create a temporary file for the downloaded database
            temp_db_path = f"{db_path}.temp"
            
            # Show progress
            self.status_label.setText("Status: Downloading backup from Google Drive...")
            self.progress_bar.setVisible(True)
            self.set_controls_enabled(False)
            
            # Store the paths for later use in the callback
            self.restore_info = {
                'db_path': db_path,
                'temp_db_path': temp_db_path,
                'current_backup': current_backup
            }
            
            # Download the file
            self.drive_handler.download_file(file_info['id'], temp_db_path)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Restore Error",
                f"Failed to start restore: {str(e)}"
            )
            self.progress_bar.setVisible(False)
            self.set_controls_enabled(True)
    
    def on_download_completed(self, success, file_path, message):
        """Handle download completion."""
        if not hasattr(self, 'restore_info'):
            self.status_label.setText("Status: Restore failed - Missing restore information")
            self.progress_bar.setVisible(False)
            self.set_controls_enabled(True)
            return
            
        if success:
            try:
                # Close database connections
                self.db_handler.Session.remove()
                self.db_handler.engine.dispose()
                
                # Replace the current database with the downloaded one
                import os
                os.replace(self.restore_info['temp_db_path'], self.restore_info['db_path'])
                
                # Signal successful restore to parent window
                self.status_label.setText("Status: Restore completed successfully")
                
                QMessageBox.information(
                    self,
                    "Restore Complete",
                    "Database successfully restored from Google Drive backup.\n\n"
                    f"A backup of your previous database was saved to:\n{self.restore_info['current_backup']}\n\n"
                    "The application will now refresh all data."
                )
                
                # Signal parent to reinitialize the database
                if hasattr(self.parent, 'reinitialize_database'):
                    self.parent.reinitialize_database()
                else:
                    # Close the dialog to force parent to reinitialize
                    self.accept()
                
            except Exception as e:
                self.status_label.setText(f"Status: Restore failed during final steps - {str(e)}")
                QMessageBox.critical(
                    self,
                    "Restore Error",
                    f"Failed during database restoration: {str(e)}\n\n"
                    f"Your original database may be at: {self.restore_info['current_backup']}"
                )
        else:
            self.status_label.setText(f"Status: Restore failed - {message}")
            QMessageBox.critical(
                self,
                "Restore Error",
                f"Failed to download backup: {message}"
            )
            
            # Clean up temp file if it exists
            if os.path.exists(self.restore_info['temp_db_path']):
                os.remove(self.restore_info['temp_db_path'])
                
        self.progress_bar.setVisible(False)
        self.set_controls_enabled(True)
        
    def on_upload_progress(self, percent):
        """Handle upload progress updates."""
        # Update progress bar
        self.progress_bar.setValue(percent)
        
        # Only update text occasionally to reduce CPU load from text rendering
        if percent % 10 == 0 or percent >= 95:
            self.status_label.setText(f"Status: Uploading backup ({percent}%)")
            
        # Process events to keep UI responsive
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
    def set_controls_enabled(self, enabled):
        """Enable or disable controls based on authentication status."""
        self.refresh_button.setEnabled(enabled)
        self.backup_button.setEnabled(enabled)
        self.restore_button.setEnabled(enabled and self.file_list.count() > 0)
        self.file_list.setEnabled(enabled) 