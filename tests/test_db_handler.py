"""
Tests for the DatabaseHandler class.
"""
import unittest
import os
import tempfile
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db_handler import DatabaseHandler
from models.schema import Base, Filament, Printer, PrinterComponent, PrintJob

class TestDatabaseHandler(unittest.TestCase):
    """Test case for the DatabaseHandler class."""
    
    def setUp(self):
        """Set up test database before each test."""
        # Create a temporary file
        self.temp_fd, self.temp_path = tempfile.mkstemp()
        os.close(self.temp_fd)  # Close file descriptor immediately
        
        # Initialize database with the temporary file path
        self.db_handler = DatabaseHandler(db_path=self.temp_path)
        
        # Create some test data
        self.test_filament_data = {
            'filament_type': 'PLA',
            'color': 'Red',
            'brand': 'TestBrand',
            'spool_weight': 1000.0,
            'quantity_remaining': 1000.0,
            'price': 25.99,
            'purchase_date': datetime.datetime.now()
        }
        
        self.test_printer_data = {
            'name': 'Test Printer',
            'model': 'Test Model',
            'notes': 'Test Notes'
        }

    def tearDown(self):
        """Clean up after each test."""
        # Close any db sessions
        self.db_handler.Session.remove()
        
        # Dispose of the engine connections
        self.db_handler.engine.dispose()
        
        # Delete the temporary file
        try:
            os.unlink(self.temp_path)
        except PermissionError:
            # If we still can't delete the file on Windows, just pass
            pass
    
    def test_add_filament(self):
        """Test adding a filament to the database."""
        # Add a filament
        filament_id = self.db_handler.add_filament(
            self.test_filament_data['filament_type'],
            self.test_filament_data['color'],
            self.test_filament_data['brand'],
            self.test_filament_data['spool_weight'],
            self.test_filament_data['quantity_remaining'],
            self.test_filament_data['price'],
            self.test_filament_data['purchase_date']
        )
        
        # Verify it was added
        session = self.db_handler.Session()
        filament = session.query(Filament).filter_by(id=filament_id).first()
        
        self.assertIsNotNone(filament)
        self.assertEqual(filament.type, self.test_filament_data['filament_type'])
        self.assertEqual(filament.color, self.test_filament_data['color'])
        self.assertEqual(filament.brand, self.test_filament_data['brand'])
        self.assertEqual(filament.spool_weight, self.test_filament_data['spool_weight'])
        self.assertEqual(filament.quantity_remaining, self.test_filament_data['quantity_remaining'])
        self.assertEqual(filament.price, self.test_filament_data['price'])
        
        # Clean up the session
        session.close()
    
    def test_get_filaments(self):
        """Test retrieving filaments from the database."""
        # Add a filament
        self.db_handler.add_filament(
            self.test_filament_data['filament_type'],
            self.test_filament_data['color'],
            self.test_filament_data['brand'],
            self.test_filament_data['spool_weight'],
            self.test_filament_data['quantity_remaining'],
            self.test_filament_data['price'],
            self.test_filament_data['purchase_date']
        )
        
        # Get all filaments
        filaments = self.db_handler.get_filaments()
        
        # Verify
        self.assertEqual(len(filaments), 1)
        self.assertEqual(filaments[0].type, self.test_filament_data['filament_type'])
        self.assertEqual(filaments[0].color, self.test_filament_data['color'])
    
    def test_update_filament_quantity(self):
        """Test updating a filament's quantity."""
        # Add a filament
        filament_id = self.db_handler.add_filament(
            self.test_filament_data['filament_type'],
            self.test_filament_data['color'],
            self.test_filament_data['brand'],
            self.test_filament_data['spool_weight'],
            self.test_filament_data['quantity_remaining'],
            self.test_filament_data['price'],
            self.test_filament_data['purchase_date']
        )
        
        # Update the quantity
        new_quantity = 800.0
        self.db_handler.update_filament_quantity(filament_id, new_quantity)
        
        # Verify
        session = self.db_handler.Session()
        filament = session.query(Filament).filter_by(id=filament_id).first()
        
        self.assertEqual(filament.quantity_remaining, new_quantity)
        
        # Clean up the session
        session.close()
    
    def test_add_printer(self):
        """Test adding a printer to the database."""
        # Add a printer
        printer_id = self.db_handler.add_printer(
            self.test_printer_data['name'],
            self.test_printer_data['model'],
            0.0,  # default power consumption
            self.test_printer_data['notes']
        )
        
        # Verify
        session = self.db_handler.Session()
        printer = session.query(Printer).filter_by(id=printer_id).first()
        
        self.assertIsNotNone(printer)
        self.assertEqual(printer.name, self.test_printer_data['name'])
        self.assertEqual(printer.model, self.test_printer_data['model'])
        self.assertEqual(printer.notes, self.test_printer_data['notes'])
        
        # Clean up the session
        session.close()
    
    def test_add_and_get_print_job(self):
        """Test adding and retrieving a print job."""
        # Add a filament and printer first
        filament_id = self.db_handler.add_filament(
            self.test_filament_data['filament_type'],
            self.test_filament_data['color'],
            self.test_filament_data['brand'],
            self.test_filament_data['spool_weight']
        )
        
        printer_id = self.db_handler.add_printer(
            self.test_printer_data['name'],
            self.test_printer_data['model']
        )
        
        # Add a print job
        job_data = {
            'project_name': 'Test Project',
            'filament_used': 100.0,
            'duration': 2.5,
            'notes': 'Test print job'
        }
        
        job_id = self.db_handler.add_print_job(
            job_data['project_name'],
            filament_id,
            printer_id,
            job_data['filament_used'],
            job_data['duration'],
            job_data['notes']
        )
        
        # Get the print jobs
        print_jobs = self.db_handler.get_print_jobs()
        
        # Verify
        self.assertEqual(len(print_jobs), 1)
        self.assertEqual(print_jobs[0].project_name, job_data['project_name'])
        self.assertEqual(print_jobs[0].filament_used, job_data['filament_used'])
        self.assertEqual(print_jobs[0].duration, job_data['duration'])
        self.assertEqual(print_jobs[0].notes, job_data['notes'])

    def test_add_printer_with_power_consumption(self):
        """Test adding a printer with power consumption data."""
        # Add a printer with power consumption
        power_consumption = 1.25  # 1.25 kWh
        printer_id = self.db_handler.add_printer(
            self.test_printer_data['name'],
            self.test_printer_data['model'],
            power_consumption,
            self.test_printer_data['notes']
        )
        
        # Verify
        session = self.db_handler.Session()
        printer = session.query(Printer).filter_by(id=printer_id).first()
        
        self.assertIsNotNone(printer)
        self.assertEqual(printer.name, self.test_printer_data['name'])
        self.assertEqual(printer.model, self.test_printer_data['model'])
        self.assertEqual(printer.power_consumption, power_consumption)
        self.assertEqual(printer.notes, self.test_printer_data['notes'])
        
        # Update power consumption
        new_power_consumption = 2.5  # 2.5 kWh
        self.db_handler.update_printer(
            printer_id=printer_id,
            power_consumption=new_power_consumption
        )
        
        # Verify update
        session = self.db_handler.Session()
        printer = session.query(Printer).filter_by(id=printer_id).first()
        self.assertEqual(printer.power_consumption, new_power_consumption)
        
        # Clean up the session
        session.close()

if __name__ == '__main__':
    unittest.main() 