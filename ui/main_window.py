"""
Main window interface for the Filament Consumption Tracker application.
"""
import os
import sys
import shutil
import datetime
import json
import tempfile
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QMessageBox, QAction, 
                            QStatusBar, QLabel, QWidget, QVBoxLayout,
                            QFileDialog, QPushButton, QApplication, QProgressBar, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

from ui.filament_tab import FilamentTab
from ui.printer_tab import PrinterTab
from ui.print_job_tab import PrintJobTab
from ui.reports_tab import ReportsTab
from ui.drive_backup_dialog import DriveBackupDialog
from ui.sync_settings_dialog import SyncSettingsDialog
from database.db_handler import DatabaseHandler

class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize database
        self.db_handler = DatabaseHandler()
        
        # Load sync settings
        self.sync_settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'database', 'sync_settings.json')
        self.sync_settings = self.load_sync_settings()
        
        # Setup UI
        self.setWindowTitle("Filament Consumption Tracker")
        self.setMinimumSize(600, 600)  # Changed from 800, 600 to be more adaptable
        self.setup_ui()
        
        # Setup auto sync timer
        self.setup_auto_sync()
        
        # Set window properties - Remove fixed size to allow responsive scaling
        self.setStyleSheet("QMainWindow {background-color: #f0f0f0;}")
        
        # Show reminder if database is empty
        self.refresh_all_data()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create central widget with tabs
        self.tabs = QTabWidget()
        
        # Create tabs
        self.filament_tab = FilamentTab(self.db_handler)
        self.printer_tab = PrinterTab(self.db_handler)
        self.print_job_tab = PrintJobTab(self.db_handler)
        self.reports_tab = ReportsTab(self.db_handler)
        
        # Set up automatic refresh mechanisms
        self.setup_auto_refresh()
        
        # Connect tab changes
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Add tabs to widget
        self.tabs.addTab(self.print_job_tab, "Print Jobs")
        self.tabs.addTab(self.filament_tab, "Filament Inventory")
        self.tabs.addTab(self.printer_tab, "Printer Management")
        self.tabs.addTab(self.reports_tab, "Reports")
        
        # Set central widget
        self.setCentralWidget(self.tabs)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Apply responsive layout settings
        self.setMinimumWidth(600)  # Reduced from previous setting
        self.tabs.setTabPosition(QTabWidget.North)  # Ensure tabs are at the top
        
        # Add a timer to check screen orientation and adjust layout
        self.orientation_timer = QTimer(self)
        self.orientation_timer.timeout.connect(self.check_screen_orientation)
        self.orientation_timer.start(1000)  # Check every second
        
    def setup_auto_refresh(self):
        """Set up automatic refresh connections between tabs."""
        # When print jobs are added/deleted/modified
        self.print_job_tab.job_updated_signal = self.on_print_job_updated
        
        # When filaments are added/deleted/modified
        if hasattr(self.filament_tab, 'filament_updated_signal'):
            self.filament_tab.filament_updated_signal = self.on_filament_updated
        else:
            # Create the signal if it doesn't exist
            self.filament_tab.filament_updated_signal = lambda: None
            
            # Connect to existing methods that modify filaments
            original_add = self.filament_tab.add_filament
            original_edit = self.filament_tab.edit_filament
            original_delete = self.filament_tab.delete_filament
            
            def wrapped_add(*args, **kwargs):
                result = original_add(*args, **kwargs)
                self.on_filament_updated()
                return result
                
            def wrapped_edit(*args, **kwargs):
                result = original_edit(*args, **kwargs)
                self.on_filament_updated()
                return result
                
            def wrapped_delete(*args, **kwargs):
                result = original_delete(*args, **kwargs)
                self.on_filament_updated()
                return result
            
            self.filament_tab.add_filament = wrapped_add
            self.filament_tab.edit_filament = wrapped_edit
            self.filament_tab.delete_filament = wrapped_delete
        
        # When printers are added/deleted/modified
        if hasattr(self.printer_tab, 'printer_updated_signal'):
            self.printer_tab.printer_updated_signal = self.on_printer_updated
        else:
            # Create the signal if it doesn't exist
            self.printer_tab.printer_updated_signal = lambda: None
            
            # Connect to existing methods that modify printers
            if hasattr(self.printer_tab, 'add_printer'):
                original_add_printer = self.printer_tab.add_printer
                
                def wrapped_add_printer(*args, **kwargs):
                    result = original_add_printer(*args, **kwargs)
                    self.on_printer_updated()
                    return result
                
                self.printer_tab.add_printer = wrapped_add_printer
    
    def on_print_job_updated(self):
        """Handle updates when print jobs change."""
        # Update filament tab data
        self.filament_tab.load_filaments()
        self.filament_tab.load_aggregated_inventory()
        self.filament_tab.load_inventory_status()
        
        # Update reports
        if hasattr(self.reports_tab, 'refresh_data') and callable(getattr(self.reports_tab, 'refresh_data')):
            self.reports_tab.refresh_data()
        
        # Show status message briefly
        self.status_bar.showMessage("Print job data updated", 3000)
    
    def on_filament_updated(self):
        """Handle updates when filaments change."""
        # Update print job tab data
        self.print_job_tab.load_filament_combo()
        
        # Update inventory displays
        self.filament_tab.load_aggregated_inventory()
        self.filament_tab.load_inventory_status()
        
        # Update reports
        if hasattr(self.reports_tab, 'refresh_data') and callable(getattr(self.reports_tab, 'refresh_data')):
            self.reports_tab.refresh_data()
        
        # Show status message briefly
        self.status_bar.showMessage("Filament data updated", 3000)
    
    def on_printer_updated(self):
        """Handle updates when printers change."""
        # Update print job tab
        self.print_job_tab.load_printer_combo()
        
        # Update reports
        if hasattr(self.reports_tab, 'refresh_data') and callable(getattr(self.reports_tab, 'refresh_data')):
            self.reports_tab.refresh_data()
        
        # Show status message briefly
        self.status_bar.showMessage("Printer data updated", 3000)

    def on_tab_changed(self, index):
        """Handle tab changes to refresh data."""
        # When switching to any tab, make sure the data is fresh
        current_tab = self.tabs.widget(index)
        
        # If switching to the print job tab, refresh filament data
        if index == 0:
            self.print_job_tab.refresh_filament_data()
            
        # If switching to the filament tab, refresh the inventory data
        elif index == 1:
            # Refresh all filament data including aggregated inventory
            self.filament_tab.load_filaments()
            self.filament_tab.load_aggregated_inventory()
            self.filament_tab.load_inventory_status()
            
        # If switching to the reports tab, refresh report data if method exists
        elif index == 3:
            # Check if the method exists before calling it
            if hasattr(self.reports_tab, 'refresh_data') and callable(getattr(self.reports_tab, 'refresh_data')):
                self.reports_tab.refresh_data()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Refresh data action
        refresh_action = QAction("&Refresh Data", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh all data from database")
        refresh_action.triggered.connect(self.refresh_all_data)
        file_menu.addAction(refresh_action)
        
        # Add backup/restore options
        file_menu.addSeparator()
        
        # Local Backup submenu
        backup_menu = file_menu.addMenu("&Local Backup")
        
        # Backup database action
        backup_action = QAction("&Backup Database to File...", self)
        backup_action.setStatusTip("Backup the database to a local file")
        backup_action.triggered.connect(self.backup_database)
        backup_menu.addAction(backup_action)
        
        # Restore database action
        restore_action = QAction("&Restore Database from File...", self)
        restore_action.setStatusTip("Restore the database from a local backup file")
        restore_action.triggered.connect(self.restore_database)
        backup_menu.addAction(restore_action)
        
        # Cloud Backup submenu
        cloud_menu = file_menu.addMenu("&Cloud Backup")
        
        # Google Drive backup action
        gdrive_action = QAction("&Google Drive Backup...", self)
        gdrive_action.setStatusTip("Backup and restore using Google Drive")
        gdrive_action.triggered.connect(self.open_gdrive_backup)
        cloud_menu.addAction(gdrive_action)
        
        sync_settings_action = QAction("Sync Settings...", self)
        sync_settings_action.triggered.connect(self.open_sync_settings)
        cloud_menu.addAction(sync_settings_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def backup_database(self):
        """Backup the database to a file."""
        try:
            # Get the current database path
            db_path = self.db_handler.engine.url.database
            
            # Set default backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"filament_tracker_backup_{timestamp}.db"
            default_path = os.path.join(os.path.expanduser("~"), "Documents", default_filename)
            
            # Ask user for backup location
            backup_path, _ = QFileDialog.getSaveFileName(
                self,
                "Backup Database",
                default_path,
                "SQLite Database (*.db);;All Files (*.*)"
            )
            
            if not backup_path:
                return  # User canceled
                
            # Create a copy of the database file
            shutil.copy2(db_path, backup_path)
            
            QMessageBox.information(
                self,
                "Backup Complete",
                f"Database successfully backed up to:\n{backup_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Failed to backup database: {str(e)}"
            )
    
    def restore_database(self):
        """Restore the database from a backup file."""
        try:
            # Ask user for backup file
            backup_path, _ = QFileDialog.getOpenFileName(
                self,
                "Restore Database",
                os.path.expanduser("~"),
                "SQLite Database (*.db);;All Files (*.*)"
            )
            
            if not backup_path:
                return  # User canceled
                
            # Confirm restoration
            reply = QMessageBox.warning(
                self,
                "Confirm Restore",
                "Restoring the database will overwrite all current data. "
                "This action cannot be undone.\n\n"
                "Are you sure you want to restore from the selected backup?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            # Get the current database path
            db_path = self.db_handler.engine.url.database
            
            # Create a backup of the current database just in case
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"{db_path}.{timestamp}.bak"
            shutil.copy2(db_path, current_backup)
            
            # Close database connections
            self.db_handler.Session.remove()
            self.db_handler.engine.dispose()
            
            # Restore backup
            shutil.copy2(backup_path, db_path)
            
            # Reinitialize database connection
            self.db_handler = DatabaseHandler()
            
            # Update tabs with new database handler
            self.filament_tab.db_handler = self.db_handler
            self.printer_tab.db_handler = self.db_handler
            self.print_job_tab.db_handler = self.db_handler
            self.reports_tab.db_handler = self.db_handler
            
            # Refresh all data
            self.refresh_all_data()
            
            QMessageBox.information(
                self,
                "Restore Complete",
                f"Database successfully restored from:\n{backup_path}\n\n"
                f"A backup of your previous database was saved to:\n{current_backup}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Restore Error",
                f"Failed to restore database: {str(e)}"
            )
        
    def refresh_all_data(self):
        """Refresh all data in all tabs."""
        # Reload data in filament tab
        self.filament_tab.load_filaments()
        self.filament_tab.load_aggregated_inventory()
        self.filament_tab.load_inventory_status()
        self.filament_tab.populate_dynamic_dropdowns()
        
        # Reload data in printer tab
        self.printer_tab.load_printers()
        self.printer_tab.load_components()
        
        # Reload data in print job tab
        self.print_job_tab.load_filament_combo()
        self.print_job_tab.load_printer_combo()
        self.print_job_tab.load_print_jobs()
        
        # Show confirmation in status bar instead of a popup
        self.status_bar.showMessage("All data refreshed", 3000)
        
    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Filament Consumption Tracker",
            """<h1>Filament Consumption Tracker</h1>
            <p>A comprehensive solution for tracking 3D printing filament usage, 
            inventory, and printer maintenance.</p>
            <p>Version 1.0</p>"""
        )
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Simplify to just ask if the user wants to exit
        reply = QMessageBox.question(
            self, 'Exit Application',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            event.ignore()
            return
            
        # If unsaved changes exist, save them automatically
        if self.filament_tab.has_unsaved_changes() or \
           self.printer_tab.has_unsaved_changes() or \
           self.print_job_tab.has_unsaved_changes():
            self.filament_tab.save_all_changes()
            self.printer_tab.save_all_changes()
            self.print_job_tab.save_all_changes()
        
        # Check if automatic sync is enabled
        if self.sync_settings.get("auto_sync_enabled", False) and \
           self.sync_settings.get("sync_frequency", "On application close") == "On application close":
            
            reply = QMessageBox.question(
                self, 'Sync to Drive',
                'Do you want to sync with Google Drive before exiting?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.backup_to_drive_and_exit(event)
                return
        
        # If we get here, just accept the event and close
        event.accept()
    
    def backup_to_drive_and_exit(self, close_event):
        """Backup database to Google Drive and then exit."""
        # Create a Google Drive handler
        from ui.google_drive_utils import GoogleDriveHandler
        drive_handler = GoogleDriveHandler()
        
        # Set up progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Backing up to Google Drive")
        progress_dialog.setModal(True)
        
        # Create layout for progress dialog
        layout = QVBoxLayout(progress_dialog)
        
        # Add message label
        message_label = QLabel("Backing up database to Google Drive...", progress_dialog)
        layout.addWidget(message_label)
        
        # Add progress bar
        progress_bar = QProgressBar(progress_dialog)
        progress_bar.setRange(0, 100)
        layout.addWidget(progress_bar)
        
        # Add cancel button
        cancel_button = QPushButton("Cancel", progress_dialog)
        cancel_button.clicked.connect(lambda: self.abort_backup_exit(progress_dialog))
        layout.addWidget(cancel_button)
        
        progress_dialog.setLayout(layout)
        progress_dialog.resize(400, 150)
        
        # Function to update message
        def update_message(msg):
            message_label.setText(msg)
        
        # Function to update progress bar
        def handle_progress(percent):
            progress_bar.setValue(percent)
        
        # Function to handle backup completion
        def handle_backup_completion(success, file_id, message):
            drive_handler.upload_completed.disconnect(handle_backup_completion)
            drive_handler.upload_progress.disconnect(handle_progress)
            
            progress_dialog.close()
            
            if success:
                # Update last sync time in settings
                self.sync_settings["last_sync"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save settings
                try:
                    os.makedirs(os.path.dirname(self.sync_settings_path), exist_ok=True)
                    with open(self.sync_settings_path, 'w') as f:
                        json.dump(self.sync_settings, f, indent=4)
                except Exception:
                    pass
                
                # Show success message
                QMessageBox.information(self, "Backup Success",
                                       f"Database successfully backed up to Google Drive.\n\n{message}")
                
                # Close the application
                close_event.accept()
            else:
                # Show error message
                reply = QMessageBox.critical(
                    self, "Backup Failed",
                    f"Failed to backup to Google Drive: {message}\n\nDo you want to exit anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    close_event.accept()
                else:
                    close_event.ignore()
        
        # Function to handle authentication completion
        def handle_auth_completion(success, message):
            drive_handler.auth_completed.disconnect(handle_auth_completion)
            
            if success:
                update_message("Authenticated with Google Drive. Preparing backup...")
                
                # Create backup file
                try:
                    # Create backup file with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"filament_tracker_backup_{timestamp}.db"
                    
                    # Use temp directory for backup file
                    temp_dir = tempfile.gettempdir()
                    backup_path = os.path.join(temp_dir, backup_filename)
                    
                    # Copy database to backup location
                    shutil.copy2(self.db_handler.db_path, backup_path)
                    
                    # Connect upload signals
                    drive_handler.upload_completed.connect(handle_backup_completion)
                    drive_handler.upload_progress.connect(handle_progress)
                    
                    # Get max backups setting
                    max_backups = self.sync_settings.get("max_backups", 5)
                    
                    # Start upload
                    update_message("Uploading database to Google Drive...")
                    app_folder = drive_handler.create_or_get_app_folder()
                    drive_handler.upload_file(backup_path, backup_filename, app_folder, max_backups=max_backups)
                    
                except Exception as e:
                    progress_dialog.close()
                    
                    # Show error message
                    reply = QMessageBox.critical(
                        self, "Backup Failed",
                        f"Failed to create backup file: {str(e)}\n\nDo you want to exit anyway?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        close_event.accept()
                    else:
                        close_event.ignore()
            else:
                progress_dialog.close()
                
                # Show error message
                reply = QMessageBox.critical(
                    self, "Authentication Failed",
                    f"Failed to authenticate with Google Drive: {message}\n\nDo you want to exit anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    close_event.accept()
                else:
                    close_event.ignore()
        
        # Connect authentication signal
        drive_handler.auth_completed.connect(handle_auth_completion)
        
        # Show progress dialog
        progress_dialog.show()
        
        # Start authentication
        if drive_handler.is_authenticated():
            # Already authenticated, trigger the completion handler directly
            handle_auth_completion(True, "Already authenticated")
        else:
            # Need to authenticate
            update_message("Authenticating with Google Drive...")
            drive_handler.authenticate(self)
    
    def abort_backup_exit(self, dialog):
        """Abort the backup and exit process."""
        dialog.close()
        QMessageBox.information(
            self,
            "Backup Cancelled",
            "Backup process cancelled. The application will not exit."
        )

    def open_gdrive_backup(self):
        """Open the Google Drive backup dialog."""
        dialog = DriveBackupDialog(self, self.db_handler)
        dialog.exec_()
        
    def reinitialize_database(self):
        """Reinitialize the database connection and refresh all data."""
        # Reinitialize database connection
        self.db_handler = DatabaseHandler()
        
        # Update tabs with new database handler
        self.filament_tab.db_handler = self.db_handler
        self.printer_tab.db_handler = self.db_handler
        self.print_job_tab.db_handler = self.db_handler
        self.reports_tab.db_handler = self.db_handler
        
        # Refresh all data
        self.refresh_all_data()

    def open_sync_settings(self):
        """Open the sync settings dialog."""
        dialog = SyncSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.sync_settings = dialog.settings
            # Update auto sync timer based on new settings
            self.update_auto_sync_timer()
    
    def load_sync_settings(self):
        """Load synchronization settings from file."""
        default_settings = {
            "auto_sync_enabled": False,
            "sync_frequency": "On application close",
            "max_backups": 5,
            "last_sync": "Never"
        }
        
        if os.path.exists(self.sync_settings_path):
            try:
                with open(self.sync_settings_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return default_settings
        return default_settings

    def setup_auto_sync(self):
        """Set up the automatic synchronization timer based on settings."""
        self.auto_sync_timer = QTimer(self)
        self.auto_sync_timer.timeout.connect(self.check_auto_sync)
        
        # Set initial timer interval based on sync frequency
        self.update_auto_sync_timer()
    
    def update_auto_sync_timer(self):
        """Update the auto sync timer based on current settings."""
        if self.sync_settings.get("auto_sync_enabled", False):
            frequency = self.sync_settings.get("sync_frequency", "On application close")
            
            if frequency == "Hourly":
                # Hourly sync (check every 10 minutes to see if an hour has passed)
                self.auto_sync_timer.start(10 * 60 * 1000)  # 10 minutes in milliseconds
            elif frequency == "Daily":
                # Daily sync (check every hour to see if a day has passed)
                self.auto_sync_timer.start(60 * 60 * 1000)  # 1 hour in milliseconds
            else:
                # On application close - stop the timer
                self.auto_sync_timer.stop()
        else:
            # Auto sync disabled - stop the timer
            self.auto_sync_timer.stop()
    
    def check_auto_sync(self):
        """Check if it's time to perform an automatic sync based on the schedule."""
        if not self.sync_settings.get("auto_sync_enabled", False):
            return
        
        frequency = self.sync_settings.get("sync_frequency", "On application close")
        last_sync_str = self.sync_settings.get("last_sync", "Never")
        
        # If never synced, do it now
        if last_sync_str == "Never":
            self.perform_auto_sync()
            return
        
        try:
            last_sync = datetime.datetime.strptime(last_sync_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.now()
            
            if frequency == "Hourly":
                # Check if an hour has passed since last sync
                if (now - last_sync).total_seconds() >= 3600:  # 3600 seconds = 1 hour
                    self.perform_auto_sync()
            elif frequency == "Daily":
                # Check if a day has passed since last sync
                if (now - last_sync).total_seconds() >= 86400:  # 86400 seconds = 1 day
                    self.perform_auto_sync()
        except Exception as e:
            print(f"Error checking auto sync schedule: {str(e)}")
    
    def perform_auto_sync(self):
        """Perform an automatic sync without user interaction."""
        # Check if there are any unsaved changes first
        if self.filament_tab.has_unsaved_changes() or \
           self.printer_tab.has_unsaved_changes() or \
           self.print_job_tab.has_unsaved_changes():
            
            # Save all changes first
            self.filament_tab.save_all_changes()
            self.printer_tab.save_all_changes()
            self.print_job_tab.save_all_changes()
        
        # Show a notification in the status bar
        self.statusBar().showMessage("Starting automatic sync to Google Drive...", 5000)
        
        # Create a Google Drive handler
        from ui.google_drive_utils import GoogleDriveHandler
        drive_handler = GoogleDriveHandler()
        
        if not drive_handler.is_authenticated():
            # Can't do auto sync without authentication
            self.statusBar().showMessage("Automatic sync failed: Not authenticated with Google Drive", 5000)
            return
        
        # Create a temporary backup file
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"filament_tracker_backup_{timestamp}.db"
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Backup the database to the temporary file
        try:
            shutil.copy2(self.db_handler.db_path, backup_path)
        except Exception as e:
            self.statusBar().showMessage(f"Automatic sync failed: {str(e)}", 5000)
            return
        
        # Get max backups setting
        max_backups = self.sync_settings.get("max_backups", 5)
        
        # Upload to Google Drive
        def handle_upload_completed(success, file_id, message):
            # Disconnect the signal
            drive_handler.upload_completed.disconnect(handle_upload_completed)
            
            if success:
                # Update last sync time
                self.sync_settings["last_sync"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save settings
                try:
                    os.makedirs(os.path.dirname(self.sync_settings_path), exist_ok=True)
                    with open(self.sync_settings_path, 'w') as f:
                        json.dump(self.sync_settings, f, indent=4)
                except Exception:
                    pass
                
                self.statusBar().showMessage("Automatic sync completed successfully", 5000)
            else:
                self.statusBar().showMessage(f"Automatic sync failed: {message}", 5000)
            
            # Clean up the temporary file
            try:
                os.remove(backup_path)
            except:
                pass
        
        # Connect the signal
        drive_handler.upload_completed.connect(handle_upload_completed)
        
        # Get the app folder ID
        app_folder_id = drive_handler.create_or_get_app_folder()
        
        # Start the upload
        drive_handler.upload_file(backup_path, backup_filename, app_folder_id, max_backups=max_backups)

    def check_screen_orientation(self):
        """Check screen orientation and adjust layout accordingly."""
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        
        # Determine if we're in portrait mode (height > width)
        is_portrait = geometry.height() > geometry.width()
        
        if is_portrait:
            # Configure for vertical orientation
            self.tabs.setTabPosition(QTabWidget.West)  # Tabs on the left side in portrait mode
            
            # Apply specific tab adjustments
            if hasattr(self.print_job_tab, 'adjust_for_portrait'):
                self.print_job_tab.adjust_for_portrait(True)
                
            if hasattr(self.filament_tab, 'adjust_for_portrait'):
                self.filament_tab.adjust_for_portrait(True)
                
            if hasattr(self.printer_tab, 'adjust_for_portrait'):
                self.printer_tab.adjust_for_portrait(True)
                
            if hasattr(self.reports_tab, 'adjust_for_portrait'):
                self.reports_tab.adjust_for_portrait(True)
        else:
            # Configure for horizontal orientation
            self.tabs.setTabPosition(QTabWidget.North)  # Tabs on top in landscape mode
            
            # Apply specific tab adjustments
            if hasattr(self.print_job_tab, 'adjust_for_portrait'):
                self.print_job_tab.adjust_for_portrait(False)
                
            if hasattr(self.filament_tab, 'adjust_for_portrait'):
                self.filament_tab.adjust_for_portrait(False)
                
            if hasattr(self.printer_tab, 'adjust_for_portrait'):
                self.printer_tab.adjust_for_portrait(False)
                
            if hasattr(self.reports_tab, 'adjust_for_portrait'):
                self.reports_tab.adjust_for_portrait(False)