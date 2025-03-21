"""
Print job management tab interface.
"""
import datetime
import csv
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel, 
                             QLineEdit, QTextEdit, QMessageBox, QInputDialog,
                             QHeaderView, QFormLayout, QDateEdit, QComboBox,
                             QDoubleSpinBox, QDateTimeEdit, QSplitter, QFileDialog,
                             QCheckBox, QFrame, QSpinBox, QMenu, QAction, QDialog,
                             QDialogButtonBox, QTabWidget)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor

from database.db_handler import DatabaseHandler

class DateTableWidgetItem(QTableWidgetItem):
    """Custom QTableWidgetItem subclass for date columns to ensure proper sorting."""
    def __lt__(self, other):
        # Compare using the timestamp data stored in UserRole
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)

class PrintJobEditDialog(QDialog):
    """Dialog for editing print job details including failure status."""
    
    def __init__(self, parent=None, db_handler=None, job_id=None):
        """Initialize print job edit dialog."""
        super().__init__(parent)
        self.db_handler = db_handler
        self.job_id = job_id
        self.job = None
        
        if job_id:
            self.job = self.db_handler.get_print_job_by_id(job_id)
            
        if not self.job:
            raise ValueError("No valid print job provided for editing")
            
        self.setup_ui()
        self.populate_data()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Edit Print Job")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Create a tab widget for organization
        tab_widget = QTabWidget()
        
        # Main information tab
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Project name
        self.project_name_input = QLineEdit()
        form_layout.addRow("Project Name:", self.project_name_input)
        
        # Date and time
        self.date_time_input = QDateTimeEdit()
        self.date_time_input.setDateTime(QDateTime.currentDateTime())
        self.date_time_input.setCalendarPopup(True)
        form_layout.addRow("Date & Time:", self.date_time_input)
        
        # Printer selector
        self.printer_combo = QComboBox()
        self.load_printer_combo()
        form_layout.addRow("Printer:", self.printer_combo)
        
        # Duration
        duration_layout = QHBoxLayout()
        self.hours_input = QSpinBox()
        self.hours_input.setRange(0, 999)
        self.hours_input.setSuffix(" hours")
        
        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setSuffix(" min")
        
        duration_layout.addWidget(self.hours_input)
        duration_layout.addWidget(self.minutes_input)
        form_layout.addRow("Print Duration:", duration_layout)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.notes_input)
        
        main_tab_layout.addLayout(form_layout)
        main_tab.setLayout(main_tab_layout)
        
        # Filament tab
        filament_tab = QWidget()
        filament_tab_layout = QVBoxLayout()
        
        # Primary filament group
        primary_filament_group = QGroupBox("Primary Filament")
        primary_filament_layout = QVBoxLayout()
        
        # Filament selection for primary filament
        primary_selection_layout = QHBoxLayout()
        
        primary_selection_layout.addWidget(QLabel("Search:"))
        self.primary_filament_search = QLineEdit()
        self.primary_filament_search.setPlaceholderText("Search filaments...")
        self.primary_filament_search.textChanged.connect(self.filter_primary_filaments)
        primary_selection_layout.addWidget(self.primary_filament_search)
        
        primary_filament_layout.addLayout(primary_selection_layout)
        
        self.filament_combo = QComboBox()
        primary_filament_layout.addWidget(self.filament_combo)
        
        # Amount of filament used
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount Used:"))
        
        self.filament_used_input = QDoubleSpinBox()
        self.filament_used_input.setRange(0.1, 10000)
        self.filament_used_input.setValue(20)  # Default value
        self.filament_used_input.setSuffix(" g")
        amount_layout.addWidget(self.filament_used_input)
        amount_layout.addStretch()
        
        primary_filament_layout.addLayout(amount_layout)
        primary_filament_group.setLayout(primary_filament_layout)
        filament_tab_layout.addWidget(primary_filament_group)
        
        # Multicolor support
        self.multicolor_checkbox = QCheckBox("Multicolor Print")
        self.multicolor_checkbox.stateChanged.connect(self.toggle_multicolor)
        filament_tab_layout.addWidget(self.multicolor_checkbox)
        
        # Secondary filaments container
        self.secondary_filaments_container = QWidget()
        secondary_filaments_layout = QVBoxLayout(self.secondary_filaments_container)
        
        # Secondary filament 1
        self.filament_group_2 = QGroupBox("Secondary Filament 1")
        filament_layout_2 = QVBoxLayout()
        
        search_layout_2 = QHBoxLayout()
        search_layout_2.addWidget(QLabel("Search:"))
        self.filament_search_2 = QLineEdit()
        self.filament_search_2.setPlaceholderText("Search filaments...")
        self.filament_search_2.textChanged.connect(lambda text: self.filter_secondary_filaments(text, 2))
        search_layout_2.addWidget(self.filament_search_2)
        
        filament_layout_2.addLayout(search_layout_2)
        
        self.filament_combo_2 = QComboBox()
        filament_layout_2.addWidget(self.filament_combo_2)
        
        amount_layout_2 = QHBoxLayout()
        amount_layout_2.addWidget(QLabel("Amount Used:"))
        
        self.filament_used_input_2 = QDoubleSpinBox()
        self.filament_used_input_2.setRange(0, 10000)
        self.filament_used_input_2.setValue(5)  # Default value
        self.filament_used_input_2.setSuffix(" g")
        amount_layout_2.addWidget(self.filament_used_input_2)
        amount_layout_2.addStretch()
        
        filament_layout_2.addLayout(amount_layout_2)
        self.filament_group_2.setLayout(filament_layout_2)
        secondary_filaments_layout.addWidget(self.filament_group_2)
        
        # Secondary filament 2
        self.filament_group_3 = QGroupBox("Secondary Filament 2")
        filament_layout_3 = QVBoxLayout()
        
        search_layout_3 = QHBoxLayout()
        search_layout_3.addWidget(QLabel("Search:"))
        self.filament_search_3 = QLineEdit()
        self.filament_search_3.setPlaceholderText("Search filaments...")
        self.filament_search_3.textChanged.connect(lambda text: self.filter_secondary_filaments(text, 3))
        search_layout_3.addWidget(self.filament_search_3)
        
        filament_layout_3.addLayout(search_layout_3)
        
        self.filament_combo_3 = QComboBox()
        filament_layout_3.addWidget(self.filament_combo_3)
        
        amount_layout_3 = QHBoxLayout()
        amount_layout_3.addWidget(QLabel("Amount Used:"))
        
        self.filament_used_input_3 = QDoubleSpinBox()
        self.filament_used_input_3.setRange(0, 10000)
        self.filament_used_input_3.setValue(0)  # Default value
        self.filament_used_input_3.setSuffix(" g")
        amount_layout_3.addWidget(self.filament_used_input_3)
        amount_layout_3.addStretch()
        
        filament_layout_3.addLayout(amount_layout_3)
        self.filament_group_3.setLayout(filament_layout_3)
        secondary_filaments_layout.addWidget(self.filament_group_3)
        
        # Secondary filament 3
        self.filament_group_4 = QGroupBox("Secondary Filament 3")
        filament_layout_4 = QVBoxLayout()
        
        search_layout_4 = QHBoxLayout()
        search_layout_4.addWidget(QLabel("Search:"))
        self.filament_search_4 = QLineEdit()
        self.filament_search_4.setPlaceholderText("Search filaments...")
        self.filament_search_4.textChanged.connect(lambda text: self.filter_secondary_filaments(text, 4))
        search_layout_4.addWidget(self.filament_search_4)
        
        filament_layout_4.addLayout(search_layout_4)
        
        self.filament_combo_4 = QComboBox()
        filament_layout_4.addWidget(self.filament_combo_4)
        
        amount_layout_4 = QHBoxLayout()
        amount_layout_4.addWidget(QLabel("Amount Used:"))
        
        self.filament_used_input_4 = QDoubleSpinBox()
        self.filament_used_input_4.setRange(0, 10000)
        self.filament_used_input_4.setValue(0)  # Default value
        self.filament_used_input_4.setSuffix(" g")
        amount_layout_4.addWidget(self.filament_used_input_4)
        amount_layout_4.addStretch()
        
        filament_layout_4.addLayout(amount_layout_4)
        self.filament_group_4.setLayout(filament_layout_4)
        secondary_filaments_layout.addWidget(self.filament_group_4)
        
        filament_tab_layout.addWidget(self.secondary_filaments_container)
        filament_tab.setLayout(filament_tab_layout)
        
        # Failure tracking tab
        failure_tab = QWidget()
        failure_layout = QVBoxLayout()
        
        # Add failure tracking group
        failure_group = QGroupBox("Mark Print as Failed")
        failure_group_layout = QVBoxLayout()
        
        self.failure_checkbox = QCheckBox("Print failed before completion")
        failure_group_layout.addWidget(self.failure_checkbox)
        
        failure_percentage_layout = QHBoxLayout()
        failure_percentage_layout.addWidget(QLabel("Failed at:"))
        
        self.failure_percentage = QSpinBox()
        self.failure_percentage.setRange(1, 99)  # 1-99% (100% would be successful)
        self.failure_percentage.setValue(50)  # Default to 50%
        self.failure_percentage.setSuffix("%")
        failure_percentage_layout.addWidget(self.failure_percentage)
        failure_percentage_layout.addStretch()
        
        failure_group_layout.addLayout(failure_percentage_layout)
        
        # Add info about filament restoration
        self.restore_info_label = QLabel()
        self.restore_info_label.setWordWrap(True)
        failure_group_layout.addWidget(self.restore_info_label)
        
        # Update restore info when percentage changes
        self.failure_percentage.valueChanged.connect(self.update_restore_info)
        self.failure_checkbox.toggled.connect(self.update_restore_info)
        
        failure_group.setLayout(failure_group_layout)
        failure_layout.addWidget(failure_group)
        failure_layout.addStretch()
        
        failure_tab.setLayout(failure_layout)
        
        # Add tabs to tab widget
        tab_widget.addTab(main_tab, "Basic Information")
        tab_widget.addTab(filament_tab, "Filament")
        tab_widget.addTab(failure_tab, "Failure Tracking")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial UI setup
        self.toggle_multicolor(False)
        self.load_filament_combo()
        self.filter_secondary_filaments("", 2)
        self.filter_secondary_filaments("", 3)
        self.filter_secondary_filaments("", 4)
        
    def load_printer_combo(self):
        """Load printers into the combo box."""
        try:
            self.printer_combo.clear()
            printers = self.db_handler.get_printers()
            
            for printer in printers:
                self.printer_combo.addItem(printer.name, printer.id)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load printers: {str(e)}")
    
    def load_filament_combo(self):
        """Load filaments into combo box."""
        try:
            self.filament_combo.clear()
            self.filament_combo_2.clear()
            self.filament_combo_3.clear()
            self.filament_combo_4.clear()
            
            # Get filaments from database
            filaments = self.db_handler.get_filaments()
            
            for filament in filaments:
                display_text = f"{filament.brand} {filament.color} {filament.type} - ID:{filament.id} ({filament.quantity_remaining:.1f}g)"
                self.filament_combo.addItem(display_text, filament.id)
                self.filament_combo_2.addItem(display_text, filament.id)
                self.filament_combo_3.addItem(display_text, filament.id)
                self.filament_combo_4.addItem(display_text, filament.id)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load filaments: {str(e)}")
    
    def filter_primary_filaments(self):
        """Filter the primary filament combo based on search text."""
        self.filter_filaments(self.primary_filament_search.text(), self.filament_combo)
    
    def filter_secondary_filaments(self, text, combo_number):
        """Filter secondary filament combos based on search text."""
        if combo_number == 2:
            self.filter_filaments(text, self.filament_combo_2)
        elif combo_number == 3:
            self.filter_filaments(text, self.filament_combo_3)
        elif combo_number == 4:
            self.filter_filaments(text, self.filament_combo_4)
    
    def filter_filaments(self, search_text, combo):
        """Filter filaments in a combo box based on search text."""
        try:
            combo.clear()
            search_text = search_text.lower()
            
            # Get filaments from database
            filaments = self.db_handler.get_filaments()
            
            for filament in filaments:
                # If search text is empty or matches any field
                if not search_text or search_text in filament.type.lower() or search_text in filament.color.lower() or search_text in filament.brand.lower():
                    display_text = f"{filament.brand} {filament.color} {filament.type} - ID:{filament.id} ({filament.quantity_remaining:.1f}g)"
                    combo.addItem(display_text, filament.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter filaments: {str(e)}")
    
    def toggle_multicolor(self, state):
        """Toggle visibility of secondary filament inputs."""
        self.secondary_filaments_container.setVisible(state)
    
    def populate_data(self):
        """Fill the form with the current job data."""
        # Set basic fields
        self.project_name_input.setText(self.job.project_name)
        self.notes_input.setPlainText(self.job.notes or "")
        
        # Set date/time
        if self.job.date:
            job_datetime = QDateTime()
            job_datetime.setSecsSinceEpoch(int(self.job.date.timestamp()))
            self.date_time_input.setDateTime(job_datetime)
        
        # Set printer
        index = self.printer_combo.findData(self.job.printer_id)
        if index >= 0:
            self.printer_combo.setCurrentIndex(index)
        
        # Set duration
        hours = int(self.job.duration)
        minutes = round((self.job.duration - hours) * 60)
        self.hours_input.setValue(hours)
        self.minutes_input.setValue(minutes)
        
        # Set primary filament
        if self.job.filament_id:
            self.select_filament_by_id(self.job.filament_id, self.filament_combo)
            self.filament_used_input.setValue(self.job.filament_used)
        
        # Check for secondary filaments
        has_secondary = (self.job.filament_id_2 is not None or 
                        self.job.filament_id_3 is not None or 
                        self.job.filament_id_4 is not None)
        
        self.multicolor_checkbox.setChecked(has_secondary)
        self.toggle_multicolor(has_secondary)
        
        # Set secondary filaments
        if self.job.filament_id_2:
            self.select_filament_by_id(self.job.filament_id_2, self.filament_combo_2)
            self.filament_used_input_2.setValue(self.job.filament_used_2 or 0)
            
        if self.job.filament_id_3:
            self.select_filament_by_id(self.job.filament_id_3, self.filament_combo_3)
            self.filament_used_input_3.setValue(self.job.filament_used_3 or 0)
            
        if self.job.filament_id_4:
            self.select_filament_by_id(self.job.filament_id_4, self.filament_combo_4)
            self.filament_used_input_4.setValue(self.job.filament_used_4 or 0)
            
        # Set failure status
        self.failure_checkbox.setChecked(self.job.is_failed == 1)
        if self.job.failure_percentage is not None:
            self.failure_percentage.setValue(int(self.job.failure_percentage))
            
        # Update restore info
        self.update_restore_info()
    
    def select_filament_by_id(self, filament_id, combo):
        """Select a filament in a combo box by its ID."""
        for i in range(combo.count()):
            if combo.itemData(i) == filament_id:
                combo.setCurrentIndex(i)
                return
    
    def update_restore_info(self):
        """Update the information about how much filament would be restored and time adjustment."""
        if not self.failure_checkbox.isChecked():
            self.restore_info_label.setText("")
            self.failure_percentage.setEnabled(False)
            return
            
        self.failure_percentage.setEnabled(True)
        
        # Only show info for prints that aren't already marked as failed
        if self.job.is_failed == 0:
            percentage = self.failure_percentage.value()
            restore_factor = (100 - percentage) / 100.0
            
            # Calculate restoration amounts for all filaments
            restoration_info = []
            
            # Primary filament
            if self.job.filament:
                amount = self.job.filament_used * restore_factor
                restoration_info.append(
                    f"{amount:.1f}g of {self.job.filament.brand} {self.job.filament.color} {self.job.filament.type}"
                )
                
            # Secondary filaments
            if self.job.filament_2 and self.job.filament_used_2:
                amount = self.job.filament_used_2 * restore_factor
                restoration_info.append(
                    f"{amount:.1f}g of {self.job.filament_2.brand} {self.job.filament_2.color} {self.job.filament_2.type}"
                )
                
            if self.job.filament_3 and self.job.filament_used_3:
                amount = self.job.filament_used_3 * restore_factor
                restoration_info.append(
                    f"{amount:.1f}g of {self.job.filament_3.brand} {self.job.filament_3.color} {self.job.filament_3.type}"
                )
                
            if self.job.filament_4 and self.job.filament_used_4:
                amount = self.job.filament_used_4 * restore_factor
                restoration_info.append(
                    f"{amount:.1f}g of {self.job.filament_4.brand} {self.job.filament_4.color} {self.job.filament_4.type}"
                )
            
            # Calculate time adjustment
            original_duration = self.job.duration
            actual_duration = original_duration * (percentage / 100.0)
            time_saved = original_duration - actual_duration
            
            # Format time saved
            hours_saved = int(time_saved)
            minutes_saved = int((time_saved - hours_saved) * 60)
            time_saved_str = f"{hours_saved}h {minutes_saved}m"
            
            # Calculate actual print duration
            actual_hours = int(actual_duration)
            actual_minutes = int((actual_duration - actual_hours) * 60)
            actual_duration_str = f"{actual_hours}h {actual_minutes}m"
            
            # Build the full info message
            info_message = ""
            
            if restoration_info:
                info_message += f"<b>The following filament will be restored to inventory:</b><br>" + "<br>".join(restoration_info) + "<br><br>"
            
            info_message += f"<b>Time adjustment:</b><br>"
            info_message += f"• Original duration: {int(original_duration)}h {int((original_duration - int(original_duration)) * 60)}m<br>"
            info_message += f"• Actual duration: {actual_duration_str} ({percentage}% of original)<br>"
            info_message += f"• Time saved: {time_saved_str}"
            
            self.restore_info_label.setText(info_message)
        else:
            self.restore_info_label.setText(
                "<i>This print is already marked as failed. Changing the percentage " +
                "will update the failure record but won't adjust filament inventory or time.</i>"
            )
    
    def get_data(self):
        """Get the form data."""
        # Calculate duration in hours
        duration = self.hours_input.value() + (self.minutes_input.value() / 60.0)
        
        # Handle secondary filaments based on multicolor checkbox
        filament_id_2 = None
        filament_used_2 = None
        filament_id_3 = None
        filament_used_3 = None
        filament_id_4 = None
        filament_used_4 = None
        
        if self.multicolor_checkbox.isChecked():
            filament_id_2 = self.filament_combo_2.currentData()
            filament_used_2 = self.filament_used_input_2.value() if filament_id_2 else None
            
            filament_id_3 = self.filament_combo_3.currentData()
            filament_used_3 = self.filament_used_input_3.value() if filament_id_3 else None
            
            filament_id_4 = self.filament_combo_4.currentData()
            filament_used_4 = self.filament_used_input_4.value() if filament_id_4 else None
        
        # Convert datetime to Python datetime
        qdt = self.date_time_input.dateTime()
        py_datetime = datetime.datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),
                                      qdt.time().hour(), qdt.time().minute(), qdt.time().second())
        
        return {
            'project_name': self.project_name_input.text().strip(),
            'printer_id': self.printer_combo.currentData(),
            'date': py_datetime,
            'filament_id': self.filament_combo.currentData(),
            'filament_used': self.filament_used_input.value(),
            'duration': duration,
            'notes': self.notes_input.toPlainText().strip(),
            'is_failed': 1 if self.failure_checkbox.isChecked() else 0,
            'failure_percentage': self.failure_percentage.value() if self.failure_checkbox.isChecked() else None,
            'filament_id_2': filament_id_2,
            'filament_used_2': filament_used_2,
            'filament_id_3': filament_id_3,
            'filament_used_3': filament_used_3,
            'filament_id_4': filament_id_4,
            'filament_used_4': filament_used_4
        }

class PrintJobTab(QWidget):
    """Print job management tab."""
    
    print_job_updated = pyqtSignal()
    
    def __init__(self, db_handler):
        """Initialize print job tab."""
        super().__init__()
        
        self.db_handler = db_handler
        # Create a placeholder for the signal that will be set by MainWindow
        self.job_updated_signal = None
        
        # Use the global electricity cost setting from the database
        self.electricity_cost_per_kwh = self.db_handler.get_electricity_cost()
        
        # Track modified items
        self.modified_print_jobs = set()
        self.modified_projects = set()
        
        # Track current orientation (default to landscape)
        self.is_portrait = False
        
        self.setup_ui()
        self.load_print_jobs()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create a splitter for form and table
        self.splitter = QSplitter(Qt.Vertical)
        
        # Top part - Add print job form
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Create form for adding new print job
        add_form_box = QGroupBox("Record New Print Job")
        form_layout = QFormLayout()
        
        # Project/model name
        self.project_name_input = QLineEdit()
        form_layout.addRow("Project Name:", self.project_name_input)
        
        # Printer selection
        self.printer_combo = QComboBox()
        form_layout.addRow("Printer:", self.printer_combo)
        
        # Primary filament section
        primary_filament_group = QGroupBox("Primary Filament")
        primary_filament_layout = QVBoxLayout()
        
        # Search field for primary filament
        primary_search_layout = QHBoxLayout()
        self.primary_filament_search = QLineEdit()
        self.primary_filament_search.setPlaceholderText("Search filament by type, color or brand...")
        self.primary_filament_search.textChanged.connect(self.filter_primary_filaments)
        primary_search_layout.addWidget(self.primary_filament_search)
        primary_filament_layout.addLayout(primary_search_layout)
        
        # Filament selection for primary filament
        self.filament_combo = QComboBox()
        self.filament_combo.currentIndexChanged.connect(self.update_filament_info)
        primary_filament_layout.addWidget(self.filament_combo)
        
        # Filament info label
        self.filament_info_label = QLabel("No filament selected")
        primary_filament_layout.addWidget(self.filament_info_label)
        
        # Amount of filament used
        primary_amount_layout = QHBoxLayout()
        self.filament_used_input = QDoubleSpinBox()
        self.filament_used_input.setRange(0.1, 10000)
        self.filament_used_input.setValue(20)  # Default value
        self.filament_used_input.setSuffix(" g")
        primary_amount_layout.addWidget(self.filament_used_input)
        primary_filament_layout.addLayout(primary_amount_layout)
        
        primary_filament_group.setLayout(primary_filament_layout)
        form_layout.addRow(primary_filament_group)
        
        # Add multicolor support with secondary filaments
        self.multicolor_checkbox = QCheckBox("Multicolor Print")
        self.multicolor_checkbox.stateChanged.connect(self.toggle_multicolor)
        
        # Add a spinner to select the number of additional filaments (1-3)
        multicolor_layout = QHBoxLayout()
        multicolor_layout.addWidget(self.multicolor_checkbox)
        
        multicolor_layout.addWidget(QLabel("Number of additional filaments:"))
        self.additional_filaments_spinner = QSpinBox()
        self.additional_filaments_spinner.setRange(1, 3)
        self.additional_filaments_spinner.setValue(1)
        self.additional_filaments_spinner.setEnabled(False)
        self.additional_filaments_spinner.valueChanged.connect(self.update_additional_filaments)
        multicolor_layout.addWidget(self.additional_filaments_spinner)
        
        form_layout.addRow(multicolor_layout)
        
        # Secondary filament section (hidden by default)
        self.secondary_filament_group = QGroupBox("Secondary Filaments")
        self.secondary_filament_group.setVisible(False)
        secondary_filament_layout = QVBoxLayout()
        
        # Second filament
        second_filament_layout = QHBoxLayout()
        self.filament_search_2 = QLineEdit()
        self.filament_search_2.setPlaceholderText("Search second filament...")
        self.filament_search_2.textChanged.connect(lambda text: self.filter_secondary_filaments(text, 2))
        second_filament_layout.addWidget(self.filament_search_2)
        secondary_filament_layout.addLayout(second_filament_layout)
        
        self.filament_combo_2 = QComboBox()
        secondary_filament_layout.addWidget(self.filament_combo_2)
        
        second_amount_layout = QHBoxLayout()
        self.filament_used_input_2 = QDoubleSpinBox()
        self.filament_used_input_2.setRange(0, 10000)
        self.filament_used_input_2.setValue(5)  # Default value
        self.filament_used_input_2.setSuffix(" g")
        second_amount_layout.addWidget(self.filament_used_input_2)
        secondary_filament_layout.addLayout(second_amount_layout)
        
        # Add a separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        secondary_filament_layout.addWidget(line)
        
        # Third filament
        third_filament_layout = QHBoxLayout()
        self.filament_search_3 = QLineEdit()
        self.filament_search_3.setPlaceholderText("Search third filament...")
        self.filament_search_3.textChanged.connect(lambda text: self.filter_secondary_filaments(text, 3))
        third_filament_layout.addWidget(self.filament_search_3)
        secondary_filament_layout.addLayout(third_filament_layout)
        
        self.filament_combo_3 = QComboBox()
        secondary_filament_layout.addWidget(self.filament_combo_3)
        
        third_amount_layout = QHBoxLayout()
        self.filament_used_input_3 = QDoubleSpinBox()
        self.filament_used_input_3.setRange(0, 10000)
        self.filament_used_input_3.setValue(0)  # Default value
        self.filament_used_input_3.setSuffix(" g")
        third_amount_layout.addWidget(self.filament_used_input_3)
        secondary_filament_layout.addLayout(third_amount_layout)
        
        # Add a separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        secondary_filament_layout.addWidget(line2)
        
        # Fourth filament
        fourth_filament_layout = QHBoxLayout()
        self.filament_search_4 = QLineEdit()
        self.filament_search_4.setPlaceholderText("Search fourth filament...")
        self.filament_search_4.textChanged.connect(lambda text: self.filter_secondary_filaments(text, 4))
        fourth_filament_layout.addWidget(self.filament_search_4)
        secondary_filament_layout.addLayout(fourth_filament_layout)
        
        self.filament_combo_4 = QComboBox()
        secondary_filament_layout.addWidget(self.filament_combo_4)
        
        fourth_amount_layout = QHBoxLayout()
        self.filament_used_input_4 = QDoubleSpinBox()
        self.filament_used_input_4.setRange(0, 10000)
        self.filament_used_input_4.setValue(0)  # Default value
        self.filament_used_input_4.setSuffix(" g")
        fourth_amount_layout.addWidget(self.filament_used_input_4)
        secondary_filament_layout.addLayout(fourth_amount_layout)
        
        self.secondary_filament_group.setLayout(secondary_filament_layout)
        form_layout.addRow(self.secondary_filament_group)
        
        # Print duration
        duration_layout = QHBoxLayout()
        
        # Hours
        self.hours_input = QSpinBox()
        self.hours_input.setRange(0, 999)
        self.hours_input.setValue(2)  # Default 2 hours
        self.hours_input.setSuffix(" h")
        duration_layout.addWidget(self.hours_input)
        
        # Minutes
        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setValue(0)  # Default 0 minutes
        self.minutes_input.setSuffix(" m")
        duration_layout.addWidget(self.minutes_input)
        
        form_layout.addRow("Print Duration:", duration_layout)
        
        # Date and time
        self.date_time_input = QDateTimeEdit()
        self.date_time_input.setDateTime(QDateTime.currentDateTime())
        self.date_time_input.setCalendarPopup(True)
        form_layout.addRow("Date & Time:", self.date_time_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("Optional notes about this print job...")
        form_layout.addRow("Notes:", self.notes_input)
        
        add_form_box.setLayout(form_layout)
        
        # Add button
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Print Job")
        self.add_button.clicked.connect(self.add_print_job)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        
        # Add form and button to top layout
        top_layout.addWidget(add_form_box)
        top_layout.addLayout(button_layout)
        
        # Bottom part - Print job history table
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Job history heading with filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Print Job History:"))
        
        # Add search box for project names
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search projects...")
        self.search_box.textChanged.connect(self.search_jobs)
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addStretch()
        
        # Filter by printer
        filter_layout.addWidget(QLabel("Filter by Printer:"))
        self.printer_filter = QComboBox()
        self.printer_filter.addItem("All Printers", None)
        self.printer_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.printer_filter)
        
        # Filter by filament type
        filter_layout.addWidget(QLabel("Filter by Filament:"))
        self.filament_filter = QComboBox()
        self.filament_filter.addItem("All Filaments", None)
        self.filament_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.filament_filter)
        
        # Add electricity cost setting
        electricity_cost_layout = QHBoxLayout()
        electricity_cost_layout.addWidget(QLabel("Electricity Cost per kWh:"))
        self.electricity_cost_input = QDoubleSpinBox()
        self.electricity_cost_input.setRange(0.01, 10.0)
        self.electricity_cost_input.setDecimals(2)
        self.electricity_cost_input.setValue(self.electricity_cost_per_kwh)
        self.electricity_cost_input.setSingleStep(0.01)
        self.electricity_cost_input.valueChanged.connect(self.update_electricity_cost)
        electricity_cost_layout.addWidget(self.electricity_cost_input)
        electricity_cost_layout.addStretch()
        bottom_layout.addLayout(electricity_cost_layout)
        
        # Create table for displaying print jobs
        self.print_job_table = QTableWidget()
        self.print_job_table.setColumnCount(8)  # Reduced to 8 columns
        self.print_job_table.setHorizontalHeaderLabels([
            "ID", "Date", "Project", "Filament", "Amount (g)", "Printer", "Duration", "Cost"
        ])
        
        # Set column widths
        self.print_job_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.print_job_table.setColumnWidth(0, 40)   # ID
        self.print_job_table.setColumnWidth(1, 120)  # Date
        self.print_job_table.setColumnWidth(2, 200)  # Project (increased for FAILED indicator)
        self.print_job_table.setColumnWidth(3, 250)  # Filament
        self.print_job_table.setColumnWidth(4, 100)  # Amount
        self.print_job_table.setColumnWidth(5, 120)  # Printer
        self.print_job_table.setColumnWidth(6, 80)   # Duration
        self.print_job_table.setColumnWidth(7, 100)  # Total Cost
        
        # Add button to delete print jobs
        delete_button_layout = QHBoxLayout()
        
        # Export button
        self.export_button = QPushButton("Export Jobs to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        delete_button_layout.addWidget(self.export_button)
        
        delete_button_layout.addStretch()
        
        # Edit button
        self.edit_job_button = QPushButton("Edit Selected Job")
        self.edit_job_button.clicked.connect(self.edit_print_job)
        delete_button_layout.addWidget(self.edit_job_button)
        
        # Delete button
        self.delete_job_button = QPushButton("Delete Selected Job")
        self.delete_job_button.clicked.connect(self.delete_print_job)
        delete_button_layout.addWidget(self.delete_job_button)
        
        # Add widgets to bottom layout
        bottom_layout.addLayout(filter_layout)
        bottom_layout.addWidget(self.print_job_table)
        bottom_layout.addLayout(delete_button_layout)
        
        # Add widgets to splitter
        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(bottom_widget)
        
        # Set initial sizes of splitter
        self.splitter.setSizes([300, 500])
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
        self.setLayout(main_layout)
        
        # Load filament and printer combos
        self.load_filament_combo()
        self.load_printer_combo()
        
        # Connect filament combo change signal
        self.filament_combo.currentIndexChanged.connect(self.update_filament_info)
        
        # Add refresh button for filament data
        form_layout.addRow("", QLabel(""))  # Add spacer
        self.refresh_filament_button = QPushButton("Refresh Filament Data")
        self.refresh_filament_button.clicked.connect(self.refresh_filament_data)
        form_layout.addRow("", self.refresh_filament_button)
        
        # Add context menu to print job table
        self.print_job_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.print_job_table.customContextMenuRequested.connect(self.show_context_menu)
        
    def adjust_for_portrait(self, is_portrait):
        """Adjust the layout for portrait or landscape orientation."""
        self.is_portrait = is_portrait
        
        if is_portrait:
            # For portrait mode (vertical monitor)
            self.splitter.setOrientation(Qt.Vertical)
            
            # Adjust table columns for narrow width
            if hasattr(self, 'print_job_table'):
                # Make sure all columns are visible but prioritize essential ones
                header = self.print_job_table.horizontalHeader()
                
                # Resize all columns to content first
                header.resizeSections(QHeaderView.ResizeToContents)
                
                # Set specific columns to have fixed or smaller widths
                date_col = 1  # Date column
                if date_col < self.print_job_table.columnCount():
                    header.setSectionResizeMode(date_col, QHeaderView.Fixed)
                    header.resizeSection(date_col, 80)
                
                # Set project name column (usually the most important) to stretch
                project_col = 2  # Project column
                if project_col < self.print_job_table.columnCount():
                    header.setSectionResizeMode(project_col, QHeaderView.Stretch)
                
                # Make amount column smaller
                amount_col = 4  # Amount column
                if amount_col < self.print_job_table.columnCount():
                    header.setSectionResizeMode(amount_col, QHeaderView.Fixed)
                    header.resizeSection(amount_col, 70)
                
                # Make cost column smaller
                cost_col = 7  # Cost column
                if cost_col < self.print_job_table.columnCount():
                    header.setSectionResizeMode(cost_col, QHeaderView.Fixed)
                    header.resizeSection(cost_col, 90)
            
            # Adjust any other widgets specific to portrait mode
            if hasattr(self, 'search_group'):
                self.search_group.setMaximumHeight(150)
        else:
            # For landscape mode (horizontal monitor)
            self.splitter.setOrientation(Qt.Vertical)
            
            # Reset table columns to default
            if hasattr(self, 'print_job_table'):
                header = self.print_job_table.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.Interactive)
                header.resizeSections(QHeaderView.ResizeToContents)
            
            # Reset any other widgets to landscape defaults
            if hasattr(self, 'search_group'):
                self.search_group.setMaximumHeight(16777215)  # Reset to default/unlimited
        
    def refresh_filament_data(self):
        """Refresh filament data from database."""
        self.load_filament_combo()
        self.update_filament_info()
    
    def load_filament_combo(self, search_text=""):
        """Load filaments into combo box with optional filtering."""
        try:
            self.filament_combo.clear()
            self.filament_combo_2.clear()
            self.filament_combo_3.clear()
            self.filament_combo_4.clear()
            
            # Get individual filaments for the combo and filter
            filaments = self.db_handler.get_filaments()
            
            # Get aggregated filament inventory for better information display
            aggregated_filaments = self.db_handler.get_aggregated_filament_inventory()
            aggregated_lookup = {}
            
            # Create a lookup for quick access to aggregated data
            for agg_filament in aggregated_filaments:
                key = (agg_filament['type'], agg_filament['color'], agg_filament['brand'])
                aggregated_lookup[key] = agg_filament
            
            filtered_filaments = []
            search_text = search_text.lower()
            
            for filament in filaments:
                # If search_text is provided, filter filaments
                if search_text and not (search_text in filament.type.lower() or 
                                        search_text in filament.color.lower() or 
                                        search_text in filament.brand.lower()):
                    continue
                
                filtered_filaments.append(filament)
                
                # Get the aggregated data for this filament type
                agg_key = (filament.type, filament.color, filament.brand)
                agg_data = aggregated_lookup.get(agg_key, {})
                total_remaining = agg_data.get('quantity_remaining', filament.quantity_remaining)
                total_quantity = agg_data.get('total_quantity', filament.spool_weight)
                spool_count = agg_data.get('spool_count', 1)
                
                # Filament display text shows individual spool and total available
                if spool_count > 1:
                    display_text = f"{filament.brand} {filament.color} {filament.type} - ID:{filament.id} ({filament.quantity_remaining:.1f}g / {total_remaining:.1f}g total)"
                else:
                    display_text = f"{filament.brand} {filament.color} {filament.type} - ID:{filament.id} ({filament.quantity_remaining:.1f}g)"
                
                self.filament_combo.addItem(display_text, filament.id)
                
                # Also add to the filter combo
                if filament.id == self.filament_filter.currentData():
                    # If this was previously selected, ensure we select it again
                    filter_text = f"{filament.type} - {filament.color}"
                    self.filament_filter.addItem(filter_text, filament.id)
                    self.filament_filter.setCurrentIndex(self.filament_filter.count() - 1)
                else:
                    filter_text = f"{filament.type} - {filament.color}"
                    self.filament_filter.addItem(filter_text, filament.id)
            
            # Load the secondary filament combos with the same filaments, but add a None option
            self.filament_combo_2.clear()
            self.filament_combo_3.clear()
            self.filament_combo_4.clear()
            
            self.filament_combo_2.addItem("None", None)
            self.filament_combo_3.addItem("None", None)
            self.filament_combo_4.addItem("None", None)
            
            for filament in filaments:
                display_text = f"{filament.brand} {filament.color} {filament.type} - ID:{filament.id} ({filament.quantity_remaining:.1f}g)"
                self.filament_combo_2.addItem(display_text, filament.id)
                self.filament_combo_3.addItem(display_text, filament.id)
                self.filament_combo_4.addItem(display_text, filament.id)
            
            # If there are filaments, update the info label for the first one
            if filtered_filaments:
                self.update_filament_info()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load filaments: {str(e)}")
    
    def update_filament_info(self):
        """Update the filament info label based on the selected filament."""
        filament_id = self.filament_combo.currentData()
        if filament_id is None:
            self.filament_info_label.setText("No filament selected")
            return
        
        try:
            # Get the individual filament data
            filaments = self.db_handler.get_filaments()
            selected_filament = None
            
            for filament in filaments:
                if filament.id == filament_id:
                    selected_filament = filament
                    break
            
            if not selected_filament:
                self.filament_info_label.setText("Filament not found in inventory")
                return
            
            # Get the aggregated inventory data
            aggregated = self.db_handler.get_aggregated_filament_inventory()
            total_info = None
            
            for agg in aggregated:
                if (agg['type'] == selected_filament.type and 
                    agg['color'] == selected_filament.color and 
                    agg['brand'] == selected_filament.brand):
                    total_info = agg
                    break
            
            if total_info:
                # Format the info label with aggregated data
                info_text = f"<b>{selected_filament.brand} {selected_filament.color} {selected_filament.type}</b>: "
                
                if total_info['spool_count'] > 1:
                    info_text += f"{total_info['quantity_remaining']:.1f}g remaining across {total_info['spool_count']} spools "
                    info_text += f"({total_info['percentage_remaining']:.1f}% of {total_info['total_quantity']:.1f}g total)"
                else:
                    info_text += f"{selected_filament.quantity_remaining:.1f}g remaining "
                    info_text += f"({(selected_filament.quantity_remaining/selected_filament.spool_weight*100):.1f}% of {selected_filament.spool_weight}g)"
                
                # Add color indicator based on remaining percentage
                if total_info['percentage_remaining'] < 20:
                    info_text = f"<span style='color:red;'>{info_text} (LOW STOCK!)</span>"
                elif total_info['percentage_remaining'] < 40:
                    info_text = f"<span style='color:orange;'>{info_text} (Running low)</span>"
                
                self.filament_info_label.setText(info_text)
            else:
                # Fallback to individual filament info
                info_text = f"{selected_filament.brand} {selected_filament.color} {selected_filament.type}: "
                info_text += f"{selected_filament.quantity_remaining:.1f}g remaining "
                percentage = (selected_filament.quantity_remaining / selected_filament.spool_weight) * 100
                info_text += f"({percentage:.1f}% of {selected_filament.spool_weight}g)"
                
                if percentage < 20:
                    info_text = f"<span style='color:red;'>{info_text} (LOW STOCK!)</span>"
                elif percentage < 40:
                    info_text = f"<span style='color:orange;'>{info_text} (Running low)</span>"
                    
                self.filament_info_label.setText(info_text)
            
        except Exception as e:
            self.filament_info_label.setText(f"Error retrieving filament info: {str(e)}")
    
    def load_printer_combo(self):
        """Load printers into combo box."""
        try:
            self.printer_combo.clear()
            self.printer_filter.clear()
            self.printer_filter.addItem("All Printers", None)
            
            printers = self.db_handler.get_printers()
            for printer in printers:
                display_text = f"{printer.name}"
                if printer.model:
                    display_text += f" ({printer.model})"
                self.printer_combo.addItem(display_text, printer.id)
                self.printer_filter.addItem(display_text, printer.id)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load printers: {str(e)}")
    
    def add_print_job(self):
        """Add a new print job to the database."""
        try:
            project_name = self.project_name_input.text().strip()
            if not project_name:
                QMessageBox.warning(self, "Input Error", "Please enter a project name.")
                return
                
            # Get filament and printer selection
            filament_id = self.filament_combo.currentData()
            if filament_id is None:
                QMessageBox.warning(self, "Input Error", "Please select a filament.")
                return
                
            printer_id = self.printer_combo.currentData()
            filament_used = self.filament_used_input.value()
            
            # Calculate duration in hours (stored as float)
            duration = self.hours_input.value() + (self.minutes_input.value() / 60.0)
            
            notes = self.notes_input.toPlainText()
            
            # Get multicolor filament data if enabled
            filament_id_2 = None
            filament_used_2 = None
            filament_id_3 = None
            filament_used_3 = None
            filament_id_4 = None
            filament_used_4 = None
            
            if self.multicolor_checkbox.isChecked():
                filament_id_2 = self.filament_combo_2.currentData()
                filament_used_2 = self.filament_used_input_2.value() if filament_id_2 else 0
                
                filament_id_3 = self.filament_combo_3.currentData()
                filament_used_3 = self.filament_used_input_3.value() if filament_id_3 else 0
                
                filament_id_4 = self.filament_combo_4.currentData()
                filament_used_4 = self.filament_used_input_4.value() if filament_id_4 else 0
            
            # Basic validation
            if not project_name:
                QMessageBox.warning(self, "Validation Error", "Project name is required.")
                return
                
            if filament_id is None:
                QMessageBox.warning(self, "Validation Error", "Please select a primary filament.")
                return
                
            if printer_id is None:
                QMessageBox.warning(self, "Validation Error", "Please select a printer.")
                return
            
            # For secondary filaments, ensure amount is provided if filament is selected
            if filament_id_2 and not filament_used_2:
                QMessageBox.warning(self, "Validation Error", "Please enter amount used for the second filament.")
                return
                
            if filament_id_3 and not filament_used_3:
                QMessageBox.warning(self, "Validation Error", "Please enter amount used for the third filament.")
                return
                
            if filament_id_4 and not filament_used_4:
                QMessageBox.warning(self, "Validation Error", "Please enter amount used for the fourth filament.")
                return
                
            # Add to database
            self.db_handler.add_print_job(
                project_name=project_name,
                filament_id=filament_id,
                printer_id=printer_id,
                filament_used=filament_used,
                duration=duration,
                notes=notes,
                filament_id_2=filament_id_2,
                filament_used_2=filament_used_2,
                filament_id_3=filament_id_3,
                filament_used_3=filament_used_3,
                filament_id_4=filament_id_4,
                filament_used_4=filament_used_4
            )
            
            # Clear form
            self.project_name_input.clear()
            self.filament_used_input.setValue(20)
            self.filament_used_input_2.setValue(5)
            self.filament_used_input_3.setValue(0)
            self.filament_used_input_4.setValue(0)
            self.hours_input.setValue(2)
            self.minutes_input.setValue(0)
            self.notes_input.clear()
            self.multicolor_checkbox.setChecked(False)
            self.additional_filaments_spinner.setValue(1)
            self.primary_filament_search.clear()
            self.filament_search_2.clear()
            self.filament_search_3.clear()
            self.filament_search_4.clear()
            
            # Reload data
            self.load_print_jobs()
            self.load_filament_combo()  # Refresh to show updated quantities
            
            # Signal to other tabs that inventory data has changed
            if self.job_updated_signal:
                self.job_updated_signal()
            
            QMessageBox.information(self, "Success", "Print job recorded successfully!")
            
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add print job: {str(e)}")
    
    def load_print_jobs(self, filament_id=None, printer_id=None, project_name=None, start_date=None, end_date=None):
        """Load print jobs from database with optional filtering."""
        try:
            # Get the latest electricity cost setting
            self.electricity_cost_per_kwh = self.db_handler.get_electricity_cost()
            
            # Save current sort state
            sort_column = self.print_job_table.horizontalHeader().sortIndicatorSection()
            sort_order = self.print_job_table.horizontalHeader().sortIndicatorOrder()
            
            # Get print jobs with optional filters
            print_jobs = self.db_handler.get_print_jobs(
                project_name=project_name,
                filament_id=filament_id,
                printer_id=printer_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Temporarily disable sorting
            self.print_job_table.setSortingEnabled(False)
            
            # Set row count
            self.print_job_table.setRowCount(len(print_jobs))
            
            for row, job in enumerate(print_jobs):
                # Set ID
                id_item = QTableWidgetItem(str(job.id))
                id_item.setData(Qt.DisplayRole, job.id)  # For proper numeric sorting
                self.print_job_table.setItem(row, 0, id_item)
                
                # Set date
                date_str = job.date.strftime("%d/%m/%y %H:%M") if job.date else "N/A"
                date_item = DateTableWidgetItem(date_str)
                date_item.setData(Qt.UserRole, job.date.timestamp() if job.date else 0)  # Store timestamp for sorting
                self.print_job_table.setItem(row, 1, date_item)
                
                # Set project name - add (FAILED) indicator if applicable
                project_name_text = job.project_name
                if job.is_failed == 1:
                    project_name_text += f" (FAILED @ {job.failure_percentage}%)"
                project_item = QTableWidgetItem(project_name_text)
                self.print_job_table.setItem(row, 2, project_item)
                
                # Set filament info - now includes multicolor information
                filament_text = f"{job.filament.brand} {job.filament.color} {job.filament.type}"
                
                # Add secondary filaments if present
                secondary_filaments = []
                
                if job.filament_id_2 and job.filament_2:
                    secondary_filaments.append(f"{job.filament_2.color} {job.filament_2.type} ({job.filament_used_2}g)")
                
                if job.filament_id_3 and job.filament_3:
                    secondary_filaments.append(f"{job.filament_3.color} {job.filament_3.type} ({job.filament_used_3}g)")
                
                if job.filament_id_4 and job.filament_4:
                    secondary_filaments.append(f"{job.filament_4.color} {job.filament_4.type} ({job.filament_used_4}g)")
                
                if secondary_filaments:
                    filament_text += f" + {', '.join(secondary_filaments)}"
                    
                self.print_job_table.setItem(row, 3, QTableWidgetItem(filament_text))
                
                # Set filament usage
                total_usage = job.filament_used
                if job.filament_used_2:
                    total_usage += job.filament_used_2
                if job.filament_used_3:
                    total_usage += job.filament_used_3
                if job.filament_used_4:
                    total_usage += job.filament_used_4
                    
                # If failed, show actual used amount vs. original planned amount
                if job.is_failed == 1 and job.failure_percentage is not None:
                    actual_usage = total_usage * (job.failure_percentage / 100.0)
                    usage_text = f"{actual_usage:.1f}g of {total_usage:.1f}g"
                else:
                    usage_text = f"{total_usage:.1f}g"
                    
                self.print_job_table.setItem(row, 4, QTableWidgetItem(usage_text))
                
                # Set printer
                self.print_job_table.setItem(row, 5, QTableWidgetItem(job.printer.name))
                
                # Set duration
                hours = int(job.duration)
                minutes = int((job.duration - hours) * 60)
                duration_str = f"{hours}h {minutes}m"
                if job.is_failed == 1:
                    duration_str += f" (Failed @ {job.failure_percentage}%)"
                self.print_job_table.setItem(row, 6, QTableWidgetItem(duration_str))
                
                # Set cost (estimated)
                material_cost = 0
                if job.filament.price and job.filament.spool_weight:
                    filament_cost_per_gram = job.filament.price / job.filament.spool_weight
                    # For failed prints, use the actual amount used
                    if job.is_failed == 1 and job.failure_percentage is not None:
                        material_cost = (job.filament_used * (job.failure_percentage / 100.0)) * filament_cost_per_gram
                    else:
                        material_cost = job.filament_used * filament_cost_per_gram
                
                # Add secondary filaments to cost if present
                if job.filament_id_2 and job.filament_2 and job.filament_used_2:
                    if job.filament_2.price and job.filament_2.spool_weight:
                        filament2_cost_per_gram = job.filament_2.price / job.filament_2.spool_weight
                        if job.is_failed == 1 and job.failure_percentage is not None:
                            material_cost += (job.filament_used_2 * (job.failure_percentage / 100.0)) * filament2_cost_per_gram
                        else:
                            material_cost += job.filament_used_2 * filament2_cost_per_gram
                
                # Add electricity cost if available
                electricity_cost = 0
                if job.printer.power_consumption and self.electricity_cost_per_kwh:
                    # For failed prints, use the actual duration based on failure percentage
                    if job.is_failed == 1 and job.failure_percentage is not None:
                        actual_duration = job.duration * (job.failure_percentage / 100.0)
                    else:
                        actual_duration = job.duration
                    electricity_cost = job.printer.power_consumption * actual_duration * self.electricity_cost_per_kwh
                
                total_cost = material_cost + electricity_cost
                cost_item = QTableWidgetItem(f"${total_cost:.2f}")
                self.print_job_table.setItem(row, 7, cost_item)
                
                # Color code failed prints
                if job.is_failed == 1:
                    for col in range(8):  # All columns
                        item = self.print_job_table.item(row, col)
                        item.setBackground(QColor(255, 200, 200))  # Light red
            
            # Re-enable sorting with previous sort settings
            self.print_job_table.setSortingEnabled(True)
            self.print_job_table.horizontalHeader().setSortIndicator(sort_column, sort_order)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load print jobs: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def search_jobs(self):
        """Search print jobs by project name."""
        search_text = self.search_box.text().strip().lower()
        
        # If search box is empty, reload with filters instead of recursively calling apply_filters
        if not search_text:
            # Get current filter values but don't call apply_filters to avoid recursion
            filament_id = self.filament_filter.currentData()
            printer_id = self.printer_filter.currentData()
            self.load_print_jobs(filament_id=filament_id, printer_id=printer_id)
            return
            
        # Otherwise, filter the table contents
        for row in range(self.print_job_table.rowCount()):
            project_name = self.print_job_table.item(row, 2).text().lower()
            filament_info = self.print_job_table.item(row, 3).text().lower()
            printer_info = self.print_job_table.item(row, 5).text().lower()
            
            if (search_text in project_name or 
                search_text in filament_info or 
                search_text in printer_info):
                self.print_job_table.setRowHidden(row, False)
            else:
                self.print_job_table.setRowHidden(row, True)
    
    def apply_filters(self):
        """Apply filters to the print job table."""
        filament_id = self.filament_filter.currentData()
        printer_id = self.printer_filter.currentData()
        
        # Load data with filters
        self.load_print_jobs(filament_id=filament_id, printer_id=printer_id)
        
        # After loading data, apply any active search filter
        # Only apply text search if there is something in the search box
        search_text = self.search_box.text().strip()
        if search_text:
            # Apply text filtering directly without recursion
            for row in range(self.print_job_table.rowCount()):
                project_name = self.print_job_table.item(row, 2).text().lower()
                filament_info = self.print_job_table.item(row, 3).text().lower()
                printer_info = self.print_job_table.item(row, 5).text().lower()
                
                if (search_text.lower() in project_name or 
                    search_text.lower() in filament_info or 
                    search_text.lower() in printer_info):
                    self.print_job_table.setRowHidden(row, False)
                else:
                    self.print_job_table.setRowHidden(row, True)
        
    def delete_print_job(self):
        """Delete the selected print job."""
        selected_rows = self.print_job_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a print job to delete.")
            return
        
        # Get the job ID from the first column of the selected row
        row = self.print_job_table.currentRow()
        job_id = int(self.print_job_table.item(row, 0).text())
        
        # Get job details for confirmation dialog
        project_name = self.print_job_table.item(row, 2).text()
        filament_used = self.print_job_table.item(row, 4).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the print job '{project_name}' ({filament_used}g of filament)?\n\n"
            "This will restore the filament amount to inventory.\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_handler.delete_print_job(job_id)
                
                # Reload the print jobs and filament combo to reflect changes
                self.load_print_jobs()
                self.load_filament_combo()
                
                # Signal to other tabs that inventory data has changed
                if self.job_updated_signal:
                    self.job_updated_signal()
                
                # Show success message with filament restoration info
                QMessageBox.information(
                    self, 
                    "Print Job Deleted",
                    f"Print job '{project_name}' has been deleted.\n\n"
                    f"The filament amount ({filament_used}g) has been restored to inventory."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete print job: {str(e)}")
    
    def export_to_csv(self):
        """Export print jobs to a CSV file."""
        try:
            # Get file save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV File", "", "CSV Files (*.csv)"
            )
            
            if not file_path:
                return  # User cancelled
                
            # Ensure the file has .csv extension
            if not file_path.endswith('.csv'):
                file_path += '.csv'
                
            # Prepare headers and rows
            rows = []
            headers = ["ID", "Date", "Project", "Filament", "Amount Used (g)", "Printer", "Duration", "Cost"]
            
            # Collect visible rows only
            for row in range(self.print_job_table.rowCount()):
                if not self.print_job_table.isRowHidden(row):
                    row_data = []
                    for col in range(8):  # Updated from 8 to 11
                        item = self.print_job_table.item(row, col)
                        if item:
                            # For cost columns, remove the $ sign
                            if col in [7]:  # Material cost, electricity cost, total cost
                                text = item.text().replace('$', '')
                            else:
                                text = item.text()
                            row_data.append(text)
                        else:
                            row_data.append("")
                    rows.append(row_data)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(rows)
                
            QMessageBox.information(self, "Success", f"Successfully exported {len(rows)} print jobs to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV: {str(e)}")
    
    def toggle_multicolor(self, state):
        """Toggle visibility of secondary filament fields."""
        is_checked = state == Qt.Checked
        self.secondary_filament_group.setVisible(is_checked)
        self.additional_filaments_spinner.setEnabled(is_checked)
        
        # Update visibility of filament fields based on spinner value
        if is_checked:
            self.update_additional_filaments(self.additional_filaments_spinner.value())
    
    def update_additional_filaments(self, value):
        """Update visibility of secondary filament fields based on spinner value."""
        # Store references to components for each filament
        filament2_components = [
            self.filament_search_2,
            self.filament_combo_2,
            self.filament_used_input_2
        ]
        
        filament3_components = [
            self.filament_search_3,
            self.filament_combo_3,
            self.filament_used_input_3
        ]
        
        filament4_components = [
            self.filament_search_4,
            self.filament_combo_4,
            self.filament_used_input_4
        ]
        
        # Show/hide components based on the spinner value
        
        # Filament 2 is always visible when multicolor is checked
        for widget in filament2_components:
            widget.setVisible(True)
            
        # First separator (between filament 2 and 3)
        try:
            # Find the first separator in the layout
            for i in range(self.secondary_filament_group.layout().count()):
                widget = self.secondary_filament_group.layout().itemAt(i).widget()
                if widget and isinstance(widget, QFrame):
                    widget.setVisible(value >= 2)
                    break
        except Exception:
            # In case of error, continue without affecting the separator
            pass
            
        # Filament 3 components
        for widget in filament3_components:
            widget.setVisible(value >= 2)
            
        # Second separator (between filament 3 and 4)
        try:
            # Find the second separator in the layout
            found_first = False
            for i in range(self.secondary_filament_group.layout().count()):
                widget = self.secondary_filament_group.layout().itemAt(i).widget()
                if widget and isinstance(widget, QFrame):
                    if found_first:
                        widget.setVisible(value >= 3)
                        break
                    else:
                        found_first = True
        except Exception:
            # In case of error, continue without affecting the separator
            pass
            
        # Filament 4 components
        for widget in filament4_components:
            widget.setVisible(value >= 3)
    
    def filter_primary_filaments(self):
        """Filter the primary filament combo based on search text."""
        search_text = self.primary_filament_search.text().lower()
        self.load_filament_combo(search_text)
    
    def filter_secondary_filaments(self, search_text, combo_number):
        """Filter the secondary filament combo boxes based on search text."""
        search_text = search_text.lower()
        combo = getattr(self, f"filament_combo_{combo_number}")
        combo.clear()
        
        try:
            # Get filaments that match the search text
            filaments = self.db_handler.get_filaments()
            combo.addItem("None", None)  # Add a None option
            
            for filament in filaments:
                # If search text is empty or matches any field
                if not search_text or search_text in filament.type.lower() or search_text in filament.color.lower() or search_text in filament.brand.lower():
                    display_text = f"{filament.brand} {filament.color} {filament.type} - ID:{filament.id} ({filament.quantity_remaining:.1f}g)"
                    combo.addItem(display_text, filament.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter filaments: {str(e)}")
    
    def update_electricity_cost(self):
        """Update the electricity cost per kWh and refresh the table."""
        self.electricity_cost_per_kwh = self.electricity_cost_input.value()
        self.load_print_jobs()  # Reload jobs to update costs
    
    def show_context_menu(self, position):
        """Display context menu for the print job table."""
        context_menu = QMenu()
        
        # Only show menu if a row is selected
        if self.print_job_table.currentRow() >= 0:
            # Edit print job action
            edit_action = QAction("Edit Print Job", self)
            edit_action.triggered.connect(self.edit_print_job)
            context_menu.addAction(edit_action)
            
            # Use as template action
            populate_action = QAction("Use as template for new job", self)
            populate_action.triggered.connect(self.populate_form_from_selected_job)
            context_menu.addAction(populate_action)
            
            context_menu.exec_(self.print_job_table.viewport().mapToGlobal(position))
    
    def edit_print_job(self):
        """Open dialog to edit the selected print job."""
        try:
            row = self.print_job_table.currentRow()
            if row < 0:
                return
                
            job_id = int(self.print_job_table.item(row, 0).text())
            
            # Open the edit dialog
            edit_dialog = PrintJobEditDialog(self, self.db_handler, job_id)
            if edit_dialog.exec_():
                # Get the updated data
                updated_data = edit_dialog.get_data()
                
                try:
                    # First handle any failed print restoration
                    failure_result = self.db_handler.update_print_job(
                        job_id=job_id,
                        project_name=updated_data['project_name'],
                        printer_id=updated_data['printer_id'],
                        notes=updated_data['notes'],
                        is_failed=updated_data['is_failed'],
                        failure_percentage=updated_data['failure_percentage']
                    )
                    
                    # Now update the full job details
                    self.db_handler.update_full_print_job(
                        job_id=job_id,
                        date=updated_data['date'],
                        duration=updated_data['duration'],
                        filament_id=updated_data['filament_id'],
                        filament_used=updated_data['filament_used'],
                        filament_id_2=updated_data['filament_id_2'],
                        filament_used_2=updated_data['filament_used_2'],
                        filament_id_3=updated_data['filament_id_3'],
                        filament_used_3=updated_data['filament_used_3'],
                        filament_id_4=updated_data['filament_id_4'],
                        filament_used_4=updated_data['filament_used_4']
                    )
                    
                    # Show a message with the results
                    if 'restored_filaments' in failure_result and failure_result['restored_filaments']:
                        # Format the restoration message
                        restoration_details = "\n".join([
                            f"• {item['restored']:.1f}g of {item['brand']} {item['color']} {item['type']}"
                            for item in failure_result['restored_filaments']
                        ])
                        
                        # Format the time adjustment message if available
                        time_message = ""
                        if 'original_duration' in failure_result and 'adjusted_duration' in failure_result:
                            original_hours = int(failure_result['original_duration'])
                            original_minutes = int((failure_result['original_duration'] - original_hours) * 60)
                            original_time_str = f"{original_hours}h {original_minutes}m"
                            
                            adjusted_hours = int(failure_result['adjusted_duration'])
                            adjusted_minutes = int((failure_result['adjusted_duration'] - adjusted_hours) * 60)
                            adjusted_time_str = f"{adjusted_hours}h {adjusted_minutes}m"
                            
                            saved_hours = int(failure_result['time_saved'])
                            saved_minutes = int((failure_result['time_saved'] - saved_hours) * 60)
                            saved_time_str = f"{saved_hours}h {saved_minutes}m"
                            
                            time_message = (
                                f"\nTime has been adjusted:\n"
                                f"• Original duration: {original_time_str}\n"
                                f"• Adjusted duration: {adjusted_time_str}\n"
                                f"• Time saved: {saved_time_str}"
                            )
                        
                        message = (
                            f"Print job marked as failed at {failure_result['failure_percentage']}%.\n\n"
                            f"The following filament has been restored to inventory:\n"
                            f"{restoration_details}\n\n"
                            f"Total restored: {failure_result['total_restored']:.1f}g"
                            f"{time_message}"
                        )
                        
                        QMessageBox.information(self, "Print Job Updated", message)
                    else:
                        QMessageBox.information(self, "Print Job Updated", 
                                               "Print job information has been updated successfully.")
                    
                    # Reload data
                    self.load_print_jobs()
                    
                    # Signal to other tabs that inventory data has changed
                    if self.job_updated_signal:
                        self.job_updated_signal()
                
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update print job: {str(e)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error editing print job: {str(e)}")
    
    def populate_form_from_selected_job(self):
        """Populate the 'Record New Print Job' form with data from the selected job."""
        try:
            row = self.print_job_table.currentRow()
            if row < 0:
                return
                
            job_id = int(self.print_job_table.item(row, 0).text())
            
            # Get the full job details from the database
            job = self.db_handler.get_print_job_by_id(job_id)
            if not job:
                QMessageBox.warning(self, "Error", "Could not retrieve job information")
                return
                
            # Populate project name
            self.project_name_input.setText(job.project_name)
            
            # Set printer
            printer_index = self.printer_combo.findData(job.printer_id)
            if printer_index >= 0:
                self.printer_combo.setCurrentIndex(printer_index)
                
            # Set filament search and select primary filament - use just the color for better search results
            if job.filament:
                # Use just the color for searching, as it's more specific and likely to match
                search_text = job.filament.color
                self.primary_filament_search.setText(search_text)
                
                # Wait for the filter to apply
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, lambda: self.select_filament_by_id(job.filament_id))
                
            # Set amount used
            self.filament_used_input.setValue(job.filament_used)
            
            # Set print duration - convert the hours float to hours and minutes
            if job.duration is not None:
                hours = int(job.duration)  # Integer part is hours
                minutes = int((job.duration - hours) * 60)  # Fractional part converted to minutes
                self.hours_input.setValue(hours)
                self.minutes_input.setValue(minutes)
                
            # Set notes
            if job.notes:
                self.notes_input.setPlainText(job.notes)
                
            # Handle multicolor print if applicable
            has_secondary_filaments = (job.filament_id_2 is not None or 
                                      job.filament_id_3 is not None or 
                                      job.filament_id_4 is not None)
            
            if has_secondary_filaments:
                self.multicolor_checkbox.setChecked(True)
                
                # Count how many additional filaments
                additional_count = 0
                if job.filament_id_2: additional_count += 1
                if job.filament_id_3: additional_count += 1
                if job.filament_id_4: additional_count += 1
                
                self.additional_filaments_spinner.setValue(additional_count)
                
                # Set secondary filaments after a short delay to let the UI update
                QTimer.singleShot(200, lambda: self.set_secondary_filaments(job))
                
            QMessageBox.information(self, "Template Applied", 
                                   "The selected job has been used as a template for the new job form.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate form: {str(e)}")
    
    def select_filament_by_id(self, filament_id):
        """Select a filament in the combo box by its ID."""
        for i in range(self.filament_combo.count()):
            if self.filament_combo.itemData(i) == filament_id:
                self.filament_combo.setCurrentIndex(i)
                return
    
    def set_secondary_filaments(self, job):
        """Set secondary filaments for a multicolor job."""
        # Second filament
        if job.filament_id_2 and job.filament_2:
            # Use just the color for searching
            search_text = job.filament_2.color
            self.filament_search_2.setText(search_text)
            
            # Find and select the filament in the combo
            for i in range(self.filament_combo_2.count()):
                if self.filament_combo_2.itemData(i) == job.filament_id_2:
                    self.filament_combo_2.setCurrentIndex(i)
                    break
                    
            self.filament_used_input_2.setValue(job.filament_used_2 or 0)
            
        # Third filament
        if job.filament_id_3 and job.filament_3:
            # Use just the color for searching
            search_text = job.filament_3.color
            self.filament_search_3.setText(search_text)
            
            # Find and select the filament in the combo
            for i in range(self.filament_combo_3.count()):
                if self.filament_combo_3.itemData(i) == job.filament_id_3:
                    self.filament_combo_3.setCurrentIndex(i)
                    break
                    
            self.filament_used_input_3.setValue(job.filament_used_3 or 0)
            
        # Fourth filament
        if job.filament_id_4 and job.filament_4:
            # Use just the color for searching
            search_text = job.filament_4.color
            self.filament_search_4.setText(search_text)
            
            # Find and select the filament in the combo
            for i in range(self.filament_combo_4.count()):
                if self.filament_combo_4.itemData(i) == job.filament_id_4:
                    self.filament_combo_4.setCurrentIndex(i)
                    break
                    
            self.filament_used_input_4.setValue(job.filament_used_4 or 0)
    
    def has_unsaved_changes(self):
        """Check if there are any unsaved changes in the print job tab."""
        return len(self.modified_print_jobs) > 0
    
    def save_all_changes(self):
        """Save all pending changes in the print job tab."""
        # Since we don't have direct save methods for each table,
        # we'll simply reload the data and emit the signal to indicate changes
        
        # Reload the data to refresh the views
        self.load_print_jobs()
        
        # Clear modification tracking
        self.modified_print_jobs.clear()
        self.modified_projects.clear()
        
        # Emit signal to notify that print job data has been updated
        self.print_job_updated.emit()
        
    def on_print_job_cell_changed(self, row, column):
        """Handle print job table cell changes."""
        if column > 0:  # Ignore ID column
            job_id = self.print_job_table.item(row, 0).data(Qt.UserRole)
            if job_id:
                self.modified_print_jobs.add(job_id)
                # Set job name in bold to indicate unsaved changes
                name_item = self.print_job_table.item(row, 1)
                if name_item:
                    font = name_item.font()
                    font.setBold(True)
                    name_item.setFont(font)
        
    def on_project_cell_changed(self, row, column):
        """Handle project table cell changes."""
        if column > 0 and column == 2:  # Project column (assuming column 2 is project)
            project_id = self.print_job_table.item(row, 2).data(Qt.UserRole)
            if project_id:
                self.modified_projects.add(project_id)
                # Set project name in bold to indicate unsaved changes
                project_item = self.print_job_table.item(row, 2)
                if project_item:
                    font = project_item.font()
                    font.setBold(True)
                    project_item.setFont(font)
    
    def connect_signals(self):
        """Connect signals to handle table cell changes."""
        # Connect print job table changes
        self.print_job_table.cellChanged.connect(self.on_print_job_cell_changed)