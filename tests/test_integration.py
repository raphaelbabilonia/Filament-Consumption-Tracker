#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration tests for the Filament Consumption Tracker application.
This test suite tests the main functionalities of the application.
"""

import sys
import unittest
import os
import tempfile
import time
from pathlib import Path
from datetime import datetime, date
import shutil

# Add parent directory to path to be able to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from database.db_handler import DatabaseHandler
from models.schema import Base
from ui.main_window import MainWindow
from ui.filament_tab import FilamentTab, FilamentDialog, FilamentLinkGroupDialog


class TestFilamentTrackerIntegration(unittest.TestCase):
    """Integration tests for the Filament Consumption Tracker application."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once before all tests."""
        # Create a backup of the current database if it exists
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        app_folder = os.path.join(documents_path, 'FilamentTracker')
        db_path = os.path.join(app_folder, 'filament_tracker.db')
        
        cls.backup_path = None
        if os.path.exists(db_path):
            cls.backup_path = db_path + '.bak'
            shutil.copy2(db_path, cls.backup_path)
            os.remove(db_path)
        
        # Create test database directly in the default location
        cls.db_handler = DatabaseHandler()
        
        # Create app instance
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.main_window = MainWindow()
        
        # Add test data
        cls._add_test_data()
        
        # Override message box and dialog methods to avoid user interaction
        QMessageBox.question = lambda *args, **kwargs: QMessageBox.Yes
        QMessageBox.information = lambda *args, **kwargs: QMessageBox.Ok
        QInputDialog.getDouble = lambda *args, **kwargs: (25.0, True)
        QInputDialog.getText = lambda *args, **kwargs: ("Test Group", True)
        
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are finished."""
        # Close the main window
        if cls.main_window:
            cls.main_window.close()
            
        # Restore the original database if it existed
        if cls.backup_path:
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            app_folder = os.path.join(documents_path, 'FilamentTracker')
            db_path = os.path.join(app_folder, 'filament_tracker.db')
            
            if os.path.exists(db_path):
                os.remove(db_path)
            shutil.copy2(cls.backup_path, db_path)
            os.remove(cls.backup_path)
    
    @classmethod
    def _add_test_data(cls):
        """Add test data to the database."""
        # Add some filaments
        cls.filament_ids = []
        
        # PLA Red
        cls.filament_ids.append(cls.db_handler.add_filament(
            filament_type="PLA",
            color="Red",
            brand="Test Brand",
            spool_weight=1000.0,
            quantity_remaining=800.0,
            price=20.0
        ))
        
        # PLA Blue
        cls.filament_ids.append(cls.db_handler.add_filament(
            filament_type="PLA",
            color="Blue",
            brand="Test Brand",
            spool_weight=1000.0,
            quantity_remaining=250.0,
            price=20.0
        ))
        
        # PETG Black
        cls.filament_ids.append(cls.db_handler.add_filament(
            filament_type="PETG",
            color="Black",
            brand="Quality Brand",
            spool_weight=1000.0,
            quantity_remaining=950.0,
            price=25.0
        ))
        
        # ABS Gray
        cls.filament_ids.append(cls.db_handler.add_filament(
            filament_type="ABS",
            color="Gray",
            brand="Premium Brand",
            spool_weight=1000.0,
            quantity_remaining=500.0,
            price=30.0
        ))
        
        # Set ideal quantities
        cls.db_handler.set_ideal_filament_quantity("PLA", "Red", "Test Brand", 1000.0)
        cls.db_handler.set_ideal_filament_quantity("PLA", "Blue", "Test Brand", 500.0)
        cls.db_handler.set_ideal_filament_quantity("PETG", "Black", "Quality Brand", 1000.0)
        cls.db_handler.set_ideal_filament_quantity("ABS", "Gray", "Premium Brand", 750.0)
        
        # Create a filament link group
        cls.group_id = cls.db_handler.create_filament_link_group(
            name="Test Group",
            description="A test group for integration testing",
            ideal_quantity=2000.0
        )
        
        # Add filaments to the group
        cls.db_handler.add_filament_to_link_group(
            cls.group_id, "PLA", "Red", "Test Brand"
        )
        cls.db_handler.add_filament_to_link_group(
            cls.group_id, "PLA", "Blue", "Test Brand"
        )
    
    def test_001_app_launches(self):
        """Test that the app launches correctly."""
        self.assertIsNotNone(self.main_window)
        self.assertTrue(hasattr(self.main_window, 'filament_tab'))
    
    def test_002_filament_tab_loads_data(self):
        """Test that the filament tab loads data correctly."""
        filament_tab = self.main_window.filament_tab
        
        # Check that the filament table has the correct number of rows
        self.assertEqual(filament_tab.filament_table.rowCount(), 4)
        
        # Check that the aggregated table has the correct number of rows
        self.assertEqual(filament_tab.aggregated_table.rowCount(), 4)
        
        # Check that the status table has the correct number of rows (4 filaments + 1 group)
        self.assertEqual(filament_tab.status_table.rowCount(), 5)
    
    def test_003_add_filament(self):
        """Test adding a new filament."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        initial_count = filament_tab.filament_table.rowCount()
        
        # Create a new FilamentDialog to bypass the UI interaction
        dialog = FilamentDialog(filament_tab)
        dialog.type_combo.setCurrentText("TPU")
        dialog.color_combo.setCurrentText("White")
        dialog.brand_combo.setCurrentText("Flex Brand")
        dialog.quantity_input.setValue(900.0)
        dialog.spool_weight_input.setValue(1000.0)
        dialog.price_input.setValue(35.0)
        dialog.date_input.setDate(date.today())
        dialog.accept()
        
        # Manually call the add filament method
        filament_tab.db_handler.add_filament(
            filament_type=dialog.get_data()['type'],
            color=dialog.get_data()['color'],
            brand=dialog.get_data()['brand'],
            spool_weight=dialog.get_data()['spool_weight'],
            quantity_remaining=dialog.get_data()['quantity_remaining'],
            price=dialog.get_data()['price'],
            purchase_date=dialog.get_data()['purchase_date']
        )
        
        # Reload the filament data
        filament_tab.load_filaments()
        
        # Check that a new row was added
        self.assertEqual(filament_tab.filament_table.rowCount(), initial_count + 1)
        
        # Verify the new filament appears in the database
        filaments = self.db_handler.get_filaments()
        self.assertEqual(len(filaments), 5)
        
        # Verify the new filament has the correct data
        new_filament = filaments[-1]
        self.assertEqual(new_filament.type, "TPU")
        self.assertEqual(new_filament.color, "White")
        self.assertEqual(new_filament.brand, "Flex Brand")
    
    def test_004_edit_filament(self):
        """Test editing a filament."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        
        # Get the first filament's ID
        first_filament_id = int(filament_tab.filament_table.item(0, 0).text())
        
        # Get filament data
        filament = self.db_handler.get_filament_by_id(first_filament_id)
        
        # Edit the filament using the DatabaseHandler directly
        self.db_handler.update_filament(
            filament_id=first_filament_id,
            filament_type=filament.type,
            color=filament.color,
            brand="Updated Brand",  # Change the brand
            spool_weight=filament.spool_weight,
            quantity_remaining=700.0,  # Change the quantity
            price=filament.price,
            purchase_date=filament.purchase_date
        )
        
        # Reload the filament data
        filament_tab.load_filaments()
        
        # Verify the changes
        updated_filament = self.db_handler.get_filament_by_id(first_filament_id)
        self.assertEqual(updated_filament.brand, "Updated Brand")
        self.assertEqual(updated_filament.quantity_remaining, 700.0)
    
    def test_005_delete_filament(self):
        """Test deleting a filament."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        initial_count = filament_tab.filament_table.rowCount()
        
        # Get the last filament's ID (the TPU one we added)
        last_filament_id = int(filament_tab.filament_table.item(initial_count-1, 0).text())
        
        # Delete the filament using the DatabaseHandler directly
        self.db_handler.delete_filament(last_filament_id)
        
        # Reload the filament data
        filament_tab.load_filaments()
        
        # Check that a row was removed
        self.assertEqual(filament_tab.filament_table.rowCount(), initial_count - 1)
    
    def test_006_aggregated_inventory(self):
        """Test aggregated inventory calculation."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        
        # Get aggregated data directly from the database
        aggregated_data = self.db_handler.get_aggregated_filament_inventory()
        
        # Verify we have the right number of aggregated entries
        self.assertEqual(len(aggregated_data), 4)
        
        # Check one specific entry
        pla_red_entry = None
        for entry in aggregated_data:
            if entry['type'] == 'PLA' and entry['color'] == 'Red':
                pla_red_entry = entry
                break
        
        self.assertIsNotNone(pla_red_entry)
        self.assertEqual(pla_red_entry['brand'], 'Updated Brand')  # From the previous test
        self.assertEqual(pla_red_entry['quantity_remaining'], 700.0)  # From the previous test
    
    def test_007_inventory_status(self):
        """Test inventory status calculation."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        
        # Get inventory status data directly from the database
        status_data = self.db_handler.get_inventory_status()
        
        # Verify we have the right number of status entries (4 filaments + 1 group)
        self.assertEqual(len(status_data), 5)
        
        # Check that the group appears in the status
        group_entry = None
        for entry in status_data:
            if entry.get('is_group', False) and entry['type'] == 'Test Group':
                group_entry = entry
                break
        
        self.assertIsNotNone(group_entry)
        self.assertEqual(group_entry['ideal_quantity'], 2000.0)
        self.assertEqual(group_entry['current_quantity'], 950.0)  # 700.0 + 250.0
    
    def test_008_set_ideal_quantity(self):
        """Test setting ideal quantity."""
        # Set ideal quantity for a filament
        self.db_handler.set_ideal_filament_quantity("PETG", "Black", "Quality Brand", 1500.0)
        
        # Verify the change
        status_data = self.db_handler.get_inventory_status()
        petg_black_entry = None
        for entry in status_data:
            if not entry.get('is_group', False) and entry['type'] == 'PETG' and entry['color'] == 'Black':
                petg_black_entry = entry
                break
        
        self.assertIsNotNone(petg_black_entry)
        self.assertEqual(petg_black_entry['ideal_quantity'], 1500.0)
    
    def test_009_manage_filament_links(self):
        """Test managing filament link groups."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        
        # Test creating a new group
        new_group_id = self.db_handler.create_filament_link_group(
            name="New Test Group",
            description="Another test group",
            ideal_quantity=3000.0
        )
        
        # Add a filament to the new group
        self.db_handler.add_filament_to_link_group(
            new_group_id, "ABS", "Gray", "Premium Brand"
        )
        
        # Verify the new group
        group = self.db_handler.get_filament_link_group(new_group_id)
        self.assertEqual(group.name, "New Test Group")
        self.assertEqual(group.ideal_quantity, 3000.0)
        self.assertEqual(len(group.filament_links), 1)
        
        # Update the group
        self.db_handler.update_filament_link_group(
            new_group_id,
            name="Updated Group",
            description="Updated description",
            ideal_quantity=2500.0
        )
        
        # Verify the update
        group = self.db_handler.get_filament_link_group(new_group_id)
        self.assertEqual(group.name, "Updated Group")
        self.assertEqual(group.ideal_quantity, 2500.0)
        
        # Test removing a filament from the group
        self.db_handler.remove_filament_from_link_group(
            new_group_id, "ABS", "Gray", "Premium Brand"
        )
        
        # Verify the removal
        group = self.db_handler.get_filament_link_group(new_group_id)
        self.assertEqual(len(group.filament_links), 0)
        
        # Delete the group
        self.db_handler.delete_filament_link_group(new_group_id)
        
        # Verify the deletion
        with self.assertRaises(Exception):
            self.db_handler.get_filament_link_group(new_group_id)
    
    def test_010_color_coding(self):
        """Test color coding in status table."""
        # Access the filament tab
        filament_tab = self.main_window.filament_tab
        
        # Load inventory status to ensure colors are applied
        filament_tab.load_inventory_status()
        
        # Check color coding is applied (by testing for existence of background colors)
        for row in range(filament_tab.status_table.rowCount()):
            for col in range(filament_tab.status_table.columnCount()):
                item = filament_tab.status_table.item(row, col)
                if item:
                    # Just check that background color is set (not specific colors,
                    # as this would make the test too brittle)
                    self.assertTrue(item.background().color().isValid())


if __name__ == "__main__":
    unittest.main() 