"""
Tests for the database schema models.
"""
import unittest
import os
import tempfile
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.schema import Base, Filament, Printer, PrinterComponent, PrintJob, FilamentIdealInventory, FilamentLinkGroup, FilamentLink

class TestSchemaModels(unittest.TestCase):
    """Test case for the database schema models."""
    
    def setUp(self):
        """Set up test database before each test."""
        # Create a temporary file
        self.temp_fd, self.temp_path = tempfile.mkstemp()
        os.close(self.temp_fd)  # Close file descriptor immediately
        
        # Create engine and tables
        self.engine = create_engine(f'sqlite:///{self.temp_path}')
        Base.metadata.create_all(self.engine)
        
        # Create session
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Clean up after each test."""
        # Close session
        self.session.close()
        
        # Dispose of the engine connections
        self.engine.dispose()
        
        # Delete the temporary file
        try:
            os.unlink(self.temp_path)
        except PermissionError:
            # If we still can't delete the file on Windows, just pass
            pass
    
    def test_filament_model(self):
        """Test the Filament model."""
        # Create a filament object
        filament = Filament(
            type='PLA',
            color='Blue',
            brand='TestBrand',
            spool_weight=1000.0,
            quantity_remaining=1000.0,
            price=25.99,
            purchase_date=datetime.datetime.now()
        )
        
        # Add to session and commit
        self.session.add(filament)
        self.session.commit()
        
        # Query and verify
        result = self.session.query(Filament).filter_by(id=filament.id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.type, 'PLA')
        self.assertEqual(result.color, 'Blue')
        self.assertEqual(result.brand, 'TestBrand')
        self.assertEqual(result.spool_weight, 1000.0)
        self.assertEqual(result.quantity_remaining, 1000.0)
        self.assertEqual(result.price, 25.99)
    
    def test_printer_model(self):
        """Test the Printer model."""
        # Create a printer object
        printer = Printer(
            name='Test Printer',
            model='Test Model',
            notes='Test Notes',
            purchase_date=datetime.datetime.now()
        )
        
        # Add to session and commit
        self.session.add(printer)
        self.session.commit()
        
        # Query and verify
        result = self.session.query(Printer).filter_by(id=printer.id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'Test Printer')
        self.assertEqual(result.model, 'Test Model')
        self.assertEqual(result.notes, 'Test Notes')
    
    def test_printer_component_model(self):
        """Test the PrinterComponent model."""
        # Create a printer first
        printer = Printer(
            name='Test Printer',
            model='Test Model'
        )
        self.session.add(printer)
        self.session.commit()
        
        # Create a printer component
        component = PrinterComponent(
            printer_id=printer.id,
            name='Nozzle',
            replacement_interval=100,
            usage_hours=0.0,
            notes='Test component'
        )
        
        # Add to session and commit
        self.session.add(component)
        self.session.commit()
        
        # Query and verify
        result = self.session.query(PrinterComponent).filter_by(id=component.id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'Nozzle')
        self.assertEqual(result.replacement_interval, 100)
        self.assertEqual(result.usage_hours, 0.0)
        self.assertEqual(result.notes, 'Test component')
        
        # Verify relationship with printer
        self.assertEqual(result.printer.id, printer.id)
        self.assertEqual(result.printer.name, 'Test Printer')
    
    def test_print_job_model(self):
        """Test the PrintJob model."""
        # Create a filament and printer first
        filament = Filament(
            type='PLA',
            color='Red',
            brand='TestBrand',
            spool_weight=1000.0,
            quantity_remaining=1000.0
        )
        
        printer = Printer(
            name='Test Printer',
            model='Test Model'
        )
        
        self.session.add_all([filament, printer])
        self.session.commit()
        
        # Create a print job
        print_job = PrintJob(
            project_name='Test Project',
            filament_id=filament.id,
            printer_id=printer.id,
            filament_used=100.0,
            duration=2.5,
            notes='Test print job'
        )
        
        # Add to session and commit
        self.session.add(print_job)
        self.session.commit()
        
        # Query and verify
        result = self.session.query(PrintJob).filter_by(id=print_job.id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.project_name, 'Test Project')
        self.assertEqual(result.filament_used, 100.0)
        self.assertEqual(result.duration, 2.5)
        self.assertEqual(result.notes, 'Test print job')
        
        # Verify relationships
        self.assertEqual(result.filament.id, filament.id)
        self.assertEqual(result.printer.id, printer.id)
    
    def test_filament_link_group_model(self):
        """Test the FilamentLinkGroup model."""
        # Create a filament link group
        link_group = FilamentLinkGroup(
            name='Test Link Group',
            description='Test description',
            ideal_quantity=2000.0
        )
        
        # Add to session and commit
        self.session.add(link_group)
        self.session.commit()
        
        # Query and verify
        result = self.session.query(FilamentLinkGroup).filter_by(id=link_group.id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'Test Link Group')
        self.assertEqual(result.description, 'Test description')
        self.assertEqual(result.ideal_quantity, 2000.0)
    
    def test_filament_link_model(self):
        """Test the FilamentLink model."""
        # Create a filament link group first
        link_group = FilamentLinkGroup(
            name='Test Link Group',
            description='Test description'
        )
        self.session.add(link_group)
        self.session.commit()
        
        # Create a filament link
        filament_link = FilamentLink(
            group_id=link_group.id,
            type='PLA',
            color='White',
            brand='TestBrand'
        )
        
        # Add to session and commit
        self.session.add(filament_link)
        self.session.commit()
        
        # Query and verify
        result = self.session.query(FilamentLink).filter_by(id=filament_link.id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.type, 'PLA')
        self.assertEqual(result.color, 'White')
        self.assertEqual(result.brand, 'TestBrand')
        
        # Verify relationship with group
        self.assertEqual(result.group.id, link_group.id)
        self.assertEqual(result.group.name, 'Test Link Group')

if __name__ == '__main__':
    unittest.main() 