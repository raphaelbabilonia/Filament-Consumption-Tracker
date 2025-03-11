"""
Tests for the Cost Analysis tab UI.
"""
import unittest
import sys
import datetime
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from ui.reports_tab import ReportsTab
from database.db_handler import DatabaseHandler
from models.schema import PrintJob, Printer, Filament


class TestCostAnalysisUI(unittest.TestCase):
    """Test case for the Cost Analysis tab UI."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication for all tests."""
        cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up a mock database handler for testing the Cost Analysis UI."""
        # Create a mock database handler
        self.db_handler = MagicMock(spec=DatabaseHandler)
        
        # Create test data
        self.create_test_data()
        
        # Create the reports tab widget
        with patch('ui.reports_tab.QMessageBox'):  # Patch QMessageBox to avoid popups
            self.reports_tab = ReportsTab(self.db_handler)
    
    def create_test_data(self):
        """Create test data for testing the Cost Analysis UI."""
        # Create test printers
        printer1 = MagicMock(spec=Printer)
        printer1.id = 1
        printer1.name = "Printer 1"
        printer1.power_consumption = 0.3  # 300W
        
        printer2 = MagicMock(spec=Printer)
        printer2.id = 2
        printer2.name = "Printer 2"
        printer2.power_consumption = 0.4  # 400W
        
        # Create test filaments
        filament1 = MagicMock(spec=Filament)
        filament1.id = 1
        filament1.type = "PLA"
        filament1.price = 25.99
        filament1.spool_weight = 1000.0
        
        filament2 = MagicMock(spec=Filament)
        filament2.id = 2
        filament2.type = "PETG"
        filament2.price = 29.99
        filament2.spool_weight = 1000.0
        
        # Create test print jobs
        job1 = MagicMock(spec=PrintJob)
        job1.id = 1
        job1.project_name = "Project A"
        job1.duration = 2.5
        job1.date = datetime.datetime.now() - datetime.timedelta(days=5)
        job1.filament_used = 100.0
        job1.filament_used_2 = 0
        job1.filament_used_3 = 0
        job1.filament_used_4 = 0
        job1.printer = printer1
        job1.filament = filament1
        job1.filament_id_2 = None
        job1.filament_id_3 = None
        job1.filament_id_4 = None
        
        job2 = MagicMock(spec=PrintJob)
        job2.id = 2
        job2.project_name = "Project B"
        job2.duration = 3.0
        job2.date = datetime.datetime.now() - datetime.timedelta(days=2)
        job2.filament_used = 150.0
        job2.filament_used_2 = 0
        job2.filament_used_3 = 0
        job2.filament_used_4 = 0
        job2.printer = printer2
        job2.filament = filament2
        job2.filament_id_2 = None
        job2.filament_id_3 = None
        job2.filament_id_4 = None
        
        job3 = MagicMock(spec=PrintJob)
        job3.id = 3
        job3.project_name = "Project A"  # Same project as job1
        job3.duration = 1.5
        job3.date = datetime.datetime.now() - datetime.timedelta(days=1)
        job3.filament_used = 80.0
        job3.filament_used_2 = 20.0
        job3.filament_used_3 = 0
        job3.filament_used_4 = 0
        job3.printer = printer1
        job3.filament = filament1
        job3.filament_2 = filament2
        job3.filament_id_2 = filament2.id
        job3.filament_id_3 = None
        job3.filament_id_4 = None
        
        # Set up the return value for get_print_jobs
        self.db_handler.get_print_jobs.return_value = [job1, job2, job3]
    
    def test_cost_analysis_tab_creation(self):
        """Test that the Cost Analysis tab can be created."""
        # Find the Cost Analysis tab
        cost_analysis_tab = self.reports_tab.cost_analysis_tab
        
        # Check that the tab exists and has the correct components
        self.assertIsNotNone(cost_analysis_tab)
        self.assertTrue(hasattr(self.reports_tab, 'cost_time_period'))
        self.assertTrue(hasattr(self.reports_tab, 'cost_electricity_input'))
        self.assertTrue(hasattr(self.reports_tab, 'cost_grouping'))
        self.assertTrue(hasattr(self.reports_tab, 'cost_table'))
        self.assertTrue(hasattr(self.reports_tab, 'cost_breakdown_canvas'))
        self.assertTrue(hasattr(self.reports_tab, 'cost_comparison_canvas'))
    
    def test_refresh_cost_analysis(self):
        """Test that the refresh_cost_analysis method updates the UI correctly."""
        # Set up test expectations
        self.reports_tab.cost_time_period.setCurrentText("All Time")
        self.reports_tab.cost_electricity_input.setValue(0.30)
        self.reports_tab.cost_grouping.setCurrentText("Project")
        
        # Call the refresh method
        with patch('ui.reports_tab.QMessageBox'):  # Patch QMessageBox to avoid popups
            self.reports_tab.refresh_cost_analysis()
        
        # Verify that the database method was called
        self.db_handler.get_print_jobs.assert_called()
        
        # Check that the table is updated correctly
        self.assertGreater(self.reports_tab.cost_table.rowCount(), 0)
        
        # With our test data, we should have 2 projects: "Project A" and "Project B"
        self.assertEqual(self.reports_tab.cost_table.rowCount(), 2)
    
    def test_cost_grouping(self):
        """Test that changing the cost grouping updates the UI correctly."""
        # Test grouping by Project
        self.reports_tab.cost_time_period.setCurrentText("All Time")
        self.reports_tab.cost_grouping.setCurrentText("Project")
        
        with patch('ui.reports_tab.QMessageBox'):
            self.reports_tab.refresh_cost_analysis()
        
        # Should have 2 projects
        self.assertEqual(self.reports_tab.cost_table.rowCount(), 2)
        
        # Test grouping by Filament Type
        self.reports_tab.cost_grouping.setCurrentText("Filament Type")
        
        with patch('ui.reports_tab.QMessageBox'):
            self.reports_tab.refresh_cost_analysis()
        
        # Should have 2 filament types: PLA and PETG
        self.assertEqual(self.reports_tab.cost_table.rowCount(), 2)
        
        # Test grouping by Printer
        self.reports_tab.cost_grouping.setCurrentText("Printer")
        
        with patch('ui.reports_tab.QMessageBox'):
            self.reports_tab.refresh_cost_analysis()
        
        # Should have 2 printers
        self.assertEqual(self.reports_tab.cost_table.rowCount(), 2)
    
    def test_time_period_filtering(self):
        """Test that changing the time period filters the data correctly."""
        # Add a job from last year to test time filtering
        old_job = MagicMock(spec=PrintJob)
        old_job.id = 4
        old_job.project_name = "Old Project"
        old_job.duration = 2.0
        old_job.date = datetime.datetime.now() - datetime.timedelta(days=400)  # More than a year ago
        old_job.filament_used = 120.0
        old_job.filament_used_2 = 0
        old_job.filament_used_3 = 0
        old_job.filament_used_4 = 0
        old_job.printer = self.db_handler.get_print_jobs.return_value[0].printer
        old_job.filament = self.db_handler.get_print_jobs.return_value[0].filament
        old_job.filament_id_2 = None
        old_job.filament_id_3 = None
        old_job.filament_id_4 = None
        
        # Add the old job to our print jobs
        print_jobs = self.db_handler.get_print_jobs.return_value + [old_job]
        self.db_handler.get_print_jobs.return_value = print_jobs
        
        # Test with "All Time"
        self.reports_tab.cost_time_period.setCurrentText("All Time")
        self.reports_tab.cost_grouping.setCurrentText("Project")
        
        with patch('ui.reports_tab.QMessageBox'):
            self.reports_tab.refresh_cost_analysis()
        
        # Should have 3 projects including the old one
        self.assertEqual(self.reports_tab.cost_table.rowCount(), 3)
        
        # Test with "This Year"
        self.reports_tab.cost_time_period.setCurrentText("This Year")
        
        # Mock get_print_jobs to filter out the old job when called with this year's date range
        def mock_get_print_jobs(start_date=None, end_date=None, **kwargs):
            if start_date:
                # Filter jobs based on date
                return [job for job in print_jobs if job.date >= start_date]
            return print_jobs
        
        self.db_handler.get_print_jobs.side_effect = mock_get_print_jobs
        
        with patch('ui.reports_tab.QMessageBox'):
            self.reports_tab.refresh_cost_analysis()
        
        # Should have 2 projects (old project filtered out)
        self.assertEqual(self.reports_tab.cost_table.rowCount(), 2)


if __name__ == "__main__":
    unittest.main() 