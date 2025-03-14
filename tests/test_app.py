#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test script for the Filament Consumption Tracker application."""

import sys
import unittest
import os
from pathlib import Path
import tempfile
import shutil
import time

# Add parent directory to path to be able to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_schema import Base
from database.db_handler import DatabaseHandler
from main import create_app
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor

class TestFilamentApp(unittest.TestCase):
    """Test case for the Filament Consumption Tracker app."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once before all tests."""
        # Create test database
        cls.db_path = tempfile.mktemp(suffix='.db')
        cls.db_handler = DatabaseHandler(cls.db_path)
        
        # Create app instance
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.main_window = create_app(cls.db_path)
        
        # Add some test data
        cls._add_test_data()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are finished."""
        # Close the main window
        if cls.main_window:
            cls.main_window.close()
            
        # Remove temp db file
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)
    
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
        
        # Set ideal quantities
        cls.db_handler.set_ideal_quantity("PLA", "Red", 1000.0)
        cls.db_handler.set_ideal_quantity("PLA", "Blue", 500.0)
        cls.db_handler.set_ideal_quantity("PETG", "Black", 1000.0)
    
    def test_001_app_launches(self):
        """Test that the app launches correctly."""
        self.assertIsNotNone(self.main_window)
    
    def test_002_db_connection(self):
        """Test that the database connection works."""
        # Get filaments
        filaments = self.db_handler.get_filaments()
        self.assertEqual(len(filaments), 3)
    
    def test_003_filament_tab_loads(self):
        """Test that the filament tab loads correctly."""
        filament_tab = self.main_window.filament_tab
        self.assertIsNotNone(filament_tab)
        
        # Check that the filament table has data
        self.assertEqual(filament_tab.filament_table.rowCount(), 3)
    
    def test_004_aggregated_inventory_loads(self):
        """Test that the aggregated inventory loads correctly."""
        filament_tab = self.main_window.filament_tab
        
        # Check that the aggregated table has data
        self.assertEqual(filament_tab.aggregated_table.rowCount(), 3)
    
    def test_005_inventory_status_loads(self):
        """Test that the inventory status loads correctly."""
        filament_tab = self.main_window.filament_tab
        
        # Check that the status table has data
        self.assertEqual(filament_tab.status_table.rowCount(), 3)
    
    def test_006_edit_filament(self):
        """Test the edit filament functionality."""
        # Get the filament by ID
        filament = self.db_handler.get_filament_by_id(self.filament_ids[0])
        self.assertIsNotNone(filament)
        
        # Modify the filament
        self.db_handler.update_filament(
            filament_id=filament.id,
            filament_type=filament.type,
            color=filament.color,
            brand=filament.brand,
            spool_weight=filament.spool_weight,
            quantity_remaining=750.0,  # Change quantity
            price=filament.price,
            purchase_date=filament.purchase_date
        )
        
        # Verify the change
        filament = self.db_handler.get_filament_by_id(self.filament_ids[0])
        self.assertEqual(filament.quantity_remaining, 750.0)
    
    def test_007_color_coding(self):
        """Test the color coding functionality."""
        filament_tab = self.main_window.filament_tab
        
        # Test the color function with different percentages
        color_0 = filament_tab._get_status_color(0)
        color_10 = filament_tab._get_status_color(10)
        color_30 = filament_tab._get_status_color(30)
        color_50 = filament_tab._get_status_color(50)
        color_70 = filament_tab._get_status_color(70)
        color_90 = filament_tab._get_status_color(90)
        
        # Verify correct colors are returned based on percentage
        self.assertEqual(color_0, filament_tab.qcolor(240, 240, 240))  # Light gray
        self.assertEqual(color_10, filament_tab.qcolor(255, 200, 200))  # Light red
        self.assertEqual(color_30, filament_tab.qcolor(255, 235, 156))  # Light orange
        self.assertEqual(color_50, filament_tab.qcolor(255, 255, 200))  # Light yellow
        self.assertEqual(color_70, filament_tab.qcolor(200, 235, 255))  # Light blue
        self.assertEqual(color_90, filament_tab.qcolor(200, 255, 200))  # Light green
    
    def test_008_status_text(self):
        """Test the status text determination functionality."""
        filament_tab = self.main_window.filament_tab
        
        # Create test data for status_row_data
        filament_tab.status_row_data = {
            'current_quantity': 0,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Out of Stock")
        
        filament_tab.status_row_data = {
            'current_quantity': 100,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Dangerous")
        
        filament_tab.status_row_data = {
            'current_quantity': 350,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Critical")
        
        filament_tab.status_row_data = {
            'current_quantity': 550,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Low")
        
        filament_tab.status_row_data = {
            'current_quantity': 750,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Adequate")
        
        filament_tab.status_row_data = {
            'current_quantity': 950,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Optimal")
        
        filament_tab.status_row_data = {
            'current_quantity': 1200,
            'ideal_quantity': 1000
        }
        self.assertEqual(filament_tab._get_status_text(0), "Overstocked")

    @staticmethod
    def qcolor(r, g, b):
        """Helper method to create a QColor for testing."""
        return QColor(r, g, b)

if __name__ == '__main__':
    unittest.main() 