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
                             QDoubleSpinBox, QDateTimeEdit, QSplitter, QFileDialog)
from PyQt5.QtCore import Qt, QDateTime

from database.db_handler import DatabaseHandler

class PrintJobTab(QWidget):
    """Print job management tab."""
    
    def __init__(self, db_handler):
        """Initialize print job tab."""
        super().__init__()
        
        self.db_handler = db_handler
        self.setup_ui()
        self.load_print_jobs()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create a splitter for form and table
        splitter = QSplitter(Qt.Vertical)
        
        # Top part - Add print job form
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Create form for adding new print job
        add_form_box = QGroupBox("Record New Print Job")
        form_layout = QFormLayout()
        
        # Project/model name
        self.project_name_input = QLineEdit()
        form_layout.addRow("Project Name:", self.project_name_input)
        
        # Filament selection
        self.filament_combo = QComboBox()
        form_layout.addRow("Filament:", self.filament_combo)
        
        # Filament info label
        self.filament_info_label = QLabel("No filament selected")
        form_layout.addRow("Inventory Status:", self.filament_info_label)
        
        # Printer selection
        self.printer_combo = QComboBox()
        form_layout.addRow("Printer:", self.printer_combo)
        
        # Amount of filament used
        self.filament_used_input = QDoubleSpinBox()
        self.filament_used_input.setRange(0.1, 10000)
        self.filament_used_input.setValue(20)  # Default value
        self.filament_used_input.setSuffix(" g")
        form_layout.addRow("Filament Used:", self.filament_used_input)
        
        # Print duration
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.1, 1000)
        self.duration_input.setValue(2)  # Default value
        self.duration_input.setSuffix(" hours")
        form_layout.addRow("Print Duration:", self.duration_input)
        
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
        
        # Create table for displaying print jobs
        self.print_job_table = QTableWidget()
        self.print_job_table.setColumnCount(8)
        self.print_job_table.setHorizontalHeaderLabels([
            "ID", "Date", "Project", "Filament", "Printer", 
            "Amount Used (g)", "Duration (h)", "Notes"
        ])
        self.print_job_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.print_job_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Add button to delete print jobs
        delete_button_layout = QHBoxLayout()
        
        # Export button
        self.export_button = QPushButton("Export Jobs to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        delete_button_layout.addWidget(self.export_button)
        
        delete_button_layout.addStretch()
        self.delete_job_button = QPushButton("Delete Selected Job")
        self.delete_job_button.clicked.connect(self.delete_print_job)
        delete_button_layout.addWidget(self.delete_job_button)
        
        # Add widgets to bottom layout
        bottom_layout.addLayout(filter_layout)
        bottom_layout.addWidget(self.print_job_table)
        bottom_layout.addLayout(delete_button_layout)
        
        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        
        # Set initial sizes of splitter
        splitter.setSizes([300, 500])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
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
        
    def refresh_filament_data(self):
        """Refresh filament data from database."""
        self.load_filament_combo()
        self.update_filament_info()
        QMessageBox.information(self, "Refresh", "Filament data has been refreshed.")
        
    def load_filament_combo(self):
        """Load filaments into combo box."""
        try:
            self.filament_combo.clear()
            self.filament_filter.clear()
            self.filament_filter.addItem("All Filaments", None)
            
            # Get individual filaments for the combo and filter
            filaments = self.db_handler.get_filaments()
            
            # Get aggregated filament inventory for better information display
            aggregated_filaments = self.db_handler.get_aggregated_filament_inventory()
            aggregated_lookup = {}
            
            # Create a lookup for quick access to aggregated data
            for agg_filament in aggregated_filaments:
                key = (agg_filament['type'], agg_filament['color'], agg_filament['brand'])
                aggregated_lookup[key] = agg_filament
            
            for filament in filaments:
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
                    display_text = f"{filament.brand} {filament.color} {filament.type} ({filament.quantity_remaining:.1f}g)"
                
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
            
            # If there are filaments, update the info label for the first one
            if filaments:
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
            # Get values from form
            project_name = self.project_name_input.text()
            filament_id = self.filament_combo.currentData()
            printer_id = self.printer_combo.currentData()
            filament_used = self.filament_used_input.value()
            duration = self.duration_input.value()
            notes = self.notes_input.toPlainText()
            
            # Basic validation
            if not project_name:
                QMessageBox.warning(self, "Validation Error", "Project name is required.")
                return
                
            if filament_id is None:
                QMessageBox.warning(self, "Validation Error", "Please select a filament.")
                return
                
            if printer_id is None:
                QMessageBox.warning(self, "Validation Error", "Please select a printer.")
                return
                
            # Add to database
            self.db_handler.add_print_job(
                project_name=project_name,
                filament_id=filament_id,
                printer_id=printer_id,
                filament_used=filament_used,
                duration=duration,
                notes=notes
            )
            
            # Clear form
            self.project_name_input.clear()
            self.filament_used_input.setValue(20)
            self.duration_input.setValue(2)
            self.notes_input.clear()
            
            # Reload data
            self.load_print_jobs()
            self.load_filament_combo()  # Refresh to show updated quantities
            
            QMessageBox.information(self, "Success", "Print job recorded successfully!")
            
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add print job: {str(e)}")
    
    def load_print_jobs(self, filament_id=None, printer_id=None):
        """Load print jobs from database and display in table."""
        try:
            # Get print jobs with optional filtering
            print_jobs = self.db_handler.get_print_jobs(
                filament_id=filament_id,
                printer_id=printer_id
            )
            
            self.print_job_table.setRowCount(len(print_jobs))
            
            for row, job in enumerate(print_jobs):
                # Set ID
                id_item = QTableWidgetItem(str(job.id))
                self.print_job_table.setItem(row, 0, id_item)
                
                # Set date
                date_str = job.date.strftime("%Y-%m-%d %H:%M") if job.date else "N/A"
                self.print_job_table.setItem(row, 1, QTableWidgetItem(date_str))
                
                # Set project name
                self.print_job_table.setItem(row, 2, QTableWidgetItem(job.project_name))
                
                # Set filament info
                filament_text = f"{job.filament.brand} {job.filament.color} {job.filament.type}"
                self.print_job_table.setItem(row, 3, QTableWidgetItem(filament_text))
                
                # Set printer name
                printer_text = job.printer.name
                if job.printer.model:
                    printer_text += f" ({job.printer.model})"
                self.print_job_table.setItem(row, 4, QTableWidgetItem(printer_text))
                
                # Set filament used
                self.print_job_table.setItem(row, 5, QTableWidgetItem(f"{job.filament_used:.1f}"))
                
                # Set duration
                self.print_job_table.setItem(row, 6, QTableWidgetItem(f"{job.duration:.1f}"))
                
                # Set notes
                self.print_job_table.setItem(row, 7, QTableWidgetItem(job.notes or ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load print jobs: {str(e)}")
    
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
            printer_info = self.print_job_table.item(row, 4).text().lower()
            
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
                printer_info = self.print_job_table.item(row, 4).text().lower()
                
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
        filament_used = self.print_job_table.item(row, 5).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the print job '{project_name}' ({filament_used} of filament)?\n\n"
            "This will restore the filament amount to inventory and adjust printer component usage hours.\n"
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
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Print job '{project_name}' deleted successfully. Filament has been restored to inventory."
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete print job: {str(e)}")
    
    def export_to_csv(self):
        """Export print jobs to a CSV file."""
        try:
            # Ask user for file location
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Export Print Jobs",
                os.path.expanduser("~/Documents/print_jobs.csv"),
                "CSV Files (*.csv)"
            )
            
            if not file_name:  # User canceled
                return
                
            # Get current data from table, respecting any filters
            rows = []
            headers = ["ID", "Date", "Project", "Filament", "Printer", 
                      "Amount Used (g)", "Duration (h)", "Notes"]
            
            # Collect visible rows only
            for row in range(self.print_job_table.rowCount()):
                if not self.print_job_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.print_job_table.columnCount()):
                        item = self.print_job_table.item(row, col)
                        row_data.append(item.text() if item is not None else "")
                    rows.append(row_data)
            
            # Write to CSV
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(rows)
                
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"{len(rows)} print job records exported to {file_name}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export print jobs: {str(e)}")