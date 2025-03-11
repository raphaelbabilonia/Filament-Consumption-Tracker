"""
Main window interface for the Filament Consumption Tracker application.
"""
import os
import shutil
import datetime
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QMessageBox, QAction, 
                            QStatusBar, QLabel, QWidget, QVBoxLayout,
                            QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from ui.filament_tab import FilamentTab
from ui.printer_tab import PrinterTab
from ui.print_job_tab import PrintJobTab
from ui.reports_tab import ReportsTab
from database.db_handler import DatabaseHandler

class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize database
        self.db_handler = DatabaseHandler()
        
        # Setup UI
        self.setWindowTitle("Filament Consumption Tracker")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        
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
        
        # Backup database action
        backup_action = QAction("&Backup Database...", self)
        backup_action.setStatusTip("Backup the database to a file")
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        # Restore database action
        restore_action = QAction("&Restore Database...", self)
        restore_action.setStatusTip("Restore the database from a backup file")
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)
        
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
        reply = QMessageBox.question(
            self, 
            "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()