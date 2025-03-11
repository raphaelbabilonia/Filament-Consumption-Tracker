"""
Basic tests for UI components.
"""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from ui.filament_tab import FilamentTab
from ui.printer_tab import PrinterTab
from ui.print_job_tab import PrintJobTab
from ui.reports_tab import ReportsTab
from database.db_handler import DatabaseHandler


class TestUIComponents(unittest.TestCase):
    """Test case for individual UI components with a mock database."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication for all tests."""
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up a mock database handler for testing UI components."""
        # Create a mock database handler with all the necessary methods
        self.db_handler = MagicMock(spec=DatabaseHandler)
        
        # Mock common database methods to return empty lists
        self.db_handler.get_filaments.return_value = []
        self.db_handler.get_printers.return_value = []
        self.db_handler.get_print_jobs.return_value = []
        self.db_handler.get_aggregated_filament_inventory.return_value = []
        self.db_handler.get_inventory_status.return_value = []
        self.db_handler.get_filament_usage_by_type.return_value = []
        self.db_handler.get_filament_usage_by_color.return_value = []
        self.db_handler.get_printer_usage_stats.return_value = []
        self.db_handler.get_ideal_filament_quantities.return_value = []
        self.db_handler.get_filament_link_groups.return_value = []
    
    def test_filament_tab_creation(self):
        """Test that the FilamentTab can be created."""
        with patch('ui.filament_tab.QMessageBox'):  # Patch QMessageBox to avoid popups
            tab = FilamentTab(self.db_handler)
            self.assertIsNotNone(tab)
            self.assertTrue(hasattr(tab, 'filament_table'))
            self.assertTrue(hasattr(tab, 'add_button'))
    
    def test_printer_tab_creation(self):
        """Test that the PrinterTab can be created."""
        with patch('ui.printer_tab.QMessageBox'):  # Patch QMessageBox to avoid popups
            tab = PrinterTab(self.db_handler)
            self.assertIsNotNone(tab)
            self.assertTrue(hasattr(tab, 'printer_table'))
            self.assertTrue(hasattr(tab, 'add_button'))
    
    def test_print_job_tab_creation(self):
        """Test that the PrintJobTab can be created."""
        with patch('ui.print_job_tab.QMessageBox'):  # Patch QMessageBox to avoid popups
            tab = PrintJobTab(self.db_handler)
            self.assertIsNotNone(tab)
            self.assertTrue(hasattr(tab, 'print_job_table'))
            self.assertTrue(hasattr(tab, 'add_button'))
    
    def test_reports_tab_creation(self):
        """Test that the ReportsTab can be created."""
        with patch('ui.reports_tab.QMessageBox'):  # Patch QMessageBox to avoid popups
            with patch('matplotlib.figure.Figure', autospec=True):  # Mock matplotlib Figure
                with patch('matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg', autospec=True):  # Mock matplotlib canvas
                    tab = ReportsTab(self.db_handler)
                    self.assertIsNotNone(tab)
                    self.assertTrue(hasattr(tab, 'tab_widget'))


if __name__ == '__main__':
    unittest.main() 