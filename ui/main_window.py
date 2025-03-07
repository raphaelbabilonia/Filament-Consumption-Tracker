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
        
        # Connect filament tab changes to print job tab
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
        self.status_bar.showMessage("Ready")
        
    def on_tab_changed(self, index):
        """Handle tab changes to refresh data."""
        # If coming from filament tab (index 1) to print job tab (index 0)
        if index == 0 and self.tabs.widget(1) == self.filament_tab:
            # Refresh the filament data in the print job tab
            self.print_job_tab.load_filament_combo()
        
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
        self.filament_tab.populate_dynamic_dropdowns()
        
        # Reload data in printer tab
        self.printer_tab.load_printers()
        self.printer_tab.load_components()
        
        # Reload data in print job tab
        self.print_job_tab.load_filament_combo()
        self.print_job_tab.load_printer_combo()
        self.print_job_tab.load_print_jobs()
        
        # Show confirmation message
        self.status_bar.showMessage("All data refreshed", 3000)
        QMessageBox.information(self, "Refresh", "All data has been refreshed.")
        
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