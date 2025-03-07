"""
Printer management tab interface.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel, 
                             QLineEdit, QTextEdit, QMessageBox, QInputDialog,
                             QHeaderView, QFormLayout, QDateEdit, QTabWidget,
                             QSpinBox, QDoubleSpinBox, QDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from database.db_handler import DatabaseHandler

class ComponentDialog(QDialog):
    """Dialog for adding printer components."""
    
    def __init__(self, parent=None, printer_id=None):
        """Initialize component dialog."""
        super().__init__(parent)
        self.printer_id = printer_id
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Add Printer Component")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Component name
        self.name_input = QLineEdit()
        form_layout.addRow("Component Name:", self.name_input)
        
        # Replacement interval (hours)
        self.interval_input = QSpinBox()
        self.interval_input.setRange(0, 10000)
        self.interval_input.setValue(500)  # Default value
        self.interval_input.setSuffix(" hours")
        form_layout.addRow("Replacement Interval:", self.interval_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes about this component...")
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.add_button = QPushButton("Add Component")
        self.add_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_data(self):
        """Get the component data from the form."""
        return {
            'name': self.name_input.text(),
            'interval': self.interval_input.value(),
            'notes': self.notes_input.toPlainText()
        }


class PrinterTab(QWidget):
    """Printer management tab."""
    
    def __init__(self, db_handler):
        """Initialize printer tab."""
        super().__init__()
        
        self.db_handler = db_handler
        self.setup_ui()
        self.load_printers()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create tabs for printers and components
        self.tab_widget = QTabWidget()
        
        # Printers tab
        printers_widget = QWidget()
        printers_layout = QVBoxLayout()
        
        # Add printer form
        add_form_box = QGroupBox("Add New Printer")
        form_layout = QFormLayout()
        
        # Printer name
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        # Printer model
        self.model_input = QLineEdit()
        form_layout.addRow("Model:", self.model_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.notes_input)
        
        add_form_box.setLayout(form_layout)
        
        # Add button
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Printer")
        self.add_button.clicked.connect(self.add_printer)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        
        # Create table for displaying printers
        self.printer_table = QTableWidget()
        self.printer_table.setColumnCount(4)
        self.printer_table.setHorizontalHeaderLabels([
            "ID", "Name", "Model", "Notes"
        ])
        self.printer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.printer_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Buttons for editing and deleting printers
        button_layout2 = QHBoxLayout()
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_printer)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_printer)
        self.add_component_button = QPushButton("Add Component")
        self.add_component_button.clicked.connect(self.add_component)
        
        button_layout2.addWidget(self.edit_button)
        button_layout2.addWidget(self.delete_button)
        button_layout2.addStretch()
        button_layout2.addWidget(self.add_component_button)
        
        # Add widgets to printers layout
        printers_layout.addWidget(add_form_box)
        printers_layout.addLayout(button_layout)
        printers_layout.addWidget(QLabel("Current Printers:"))
        printers_layout.addWidget(self.printer_table)
        printers_layout.addLayout(button_layout2)
        
        printers_widget.setLayout(printers_layout)
        
        # Components tab
        components_widget = QWidget()
        components_layout = QVBoxLayout()
        
        # Create table for displaying components
        self.component_table = QTableWidget()
        self.component_table.setColumnCount(6)
        self.component_table.setHorizontalHeaderLabels([
            "ID", "Printer", "Component", "Installation Date", 
            "Usage (hours)", "Replacement Interval"
        ])
        self.component_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.component_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        components_layout.addWidget(QLabel("Printer Components:"))
        components_layout.addWidget(self.component_table)
        
        # Component action buttons
        component_button_layout = QHBoxLayout()
        
        self.reset_usage_button = QPushButton("Reset Usage")
        self.reset_usage_button.clicked.connect(self.reset_component_usage)
        
        self.remove_component_button = QPushButton("Remove Component")
        self.remove_component_button.clicked.connect(self.remove_component)
        
        component_button_layout.addWidget(self.reset_usage_button)
        component_button_layout.addWidget(self.remove_component_button)
        component_button_layout.addStretch()
        
        components_layout.addLayout(component_button_layout)
        components_widget.setLayout(components_layout)
        
        # Add tabs
        self.tab_widget.addTab(printers_widget, "Printers")
        self.tab_widget.addTab(components_widget, "Components")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        self.setLayout(main_layout)
        
    def tab_changed(self, index):
        """Handle tab changes to refresh data."""
        if index == 1:  # Components tab
            self.load_components()
    
    def load_printers(self):
        """Load printers from database and display in table."""
        try:
            printers = self.db_handler.get_printers()
            self.printer_table.setRowCount(len(printers))
            
            for row, printer in enumerate(printers):
                # Set ID
                id_item = QTableWidgetItem(str(printer.id))
                self.printer_table.setItem(row, 0, id_item)
                
                # Set printer details
                self.printer_table.setItem(row, 1, QTableWidgetItem(printer.name))
                self.printer_table.setItem(row, 2, QTableWidgetItem(printer.model or ""))
                self.printer_table.setItem(row, 3, QTableWidgetItem(printer.notes or ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load printers: {str(e)}")
    
    def load_components(self):
        """Load printer components from database and display in table."""
        try:
            components = self.db_handler.get_printer_components()
            self.component_table.setRowCount(len(components))
            
            for row, component in enumerate(components):
                # Set ID
                id_item = QTableWidgetItem(str(component.id))
                self.component_table.setItem(row, 0, id_item)
                
                # Set printer name
                self.component_table.setItem(row, 1, QTableWidgetItem(component.printer.name))
                
                # Set component details
                self.component_table.setItem(row, 2, QTableWidgetItem(component.name))
                
                # Format date
                date_str = component.installation_date.strftime("%Y-%m-%d") if component.installation_date else "N/A"
                self.component_table.setItem(row, 3, QTableWidgetItem(date_str))
                
                # Usage hours
                self.component_table.setItem(row, 4, QTableWidgetItem(f"{component.usage_hours:.1f}"))
                
                # Replacement interval
                interval_text = f"{component.replacement_interval} hours" if component.replacement_interval else "N/A"
                self.component_table.setItem(row, 5, QTableWidgetItem(interval_text))
                
                # Color code components that are due for replacement
                if (component.replacement_interval is not None and 
                    component.usage_hours >= component.replacement_interval):
                    for col in range(1, 6):
                        item = self.component_table.item(row, col)
                        item.setBackground(QColor(255, 200, 200))  # Light red
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load components: {str(e)}")
    
    def add_printer(self):
        """Add a new printer to the database."""
        try:
            name = self.name_input.text()
            model = self.model_input.text()
            notes = self.notes_input.toPlainText()
            
            # Basic validation
            if not name:
                QMessageBox.warning(self, "Validation Error", "Printer name is required.")
                return
                
            # Add to database
            self.db_handler.add_printer(
                name=name,
                model=model,
                notes=notes
            )
            
            # Clear inputs
            self.name_input.clear()
            self.model_input.clear()
            self.notes_input.clear()
            
            # Reload table
            self.load_printers()
            
            QMessageBox.information(self, "Success", "Printer added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add printer: {str(e)}")
    
    def edit_printer(self):
        """Edit the selected printer."""
        selected_rows = self.printer_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a printer to edit.")
            return
            
        # Get the printer ID from the first column of the selected row
        row = self.printer_table.currentRow()
        printer_id = int(self.printer_table.item(row, 0).text())
        current_name = self.printer_table.item(row, 1).text()
        current_model = self.printer_table.item(row, 2).text()
        current_notes = self.printer_table.item(row, 3).text()
        
        # Get new name
        name, ok = QInputDialog.getText(
            self, "Edit Printer", "Enter new printer name:", text=current_name
        )
        if not ok or not name:
            return
            
        # Get new model
        model, ok = QInputDialog.getText(
            self, "Edit Printer", "Enter new model:", text=current_model
        )
        if not ok:
            return
            
        # Get new notes
        notes, ok = QInputDialog.getText(
            self, "Edit Printer", "Enter new notes:", text=current_notes
        )
        if not ok:
            notes = current_notes
            
        try:
            self.db_handler.update_printer(
                printer_id=printer_id,
                name=name,
                model=model,
                notes=notes
            )
            self.load_printers()
            QMessageBox.information(self, "Success", "Printer updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update printer: {str(e)}")
    
    def delete_printer(self):
        """Delete the selected printer."""
        selected_rows = self.printer_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a printer to delete.")
            return
            
        # Get the printer ID from the first column of the selected row
        row = self.printer_table.currentRow()
        printer_id = int(self.printer_table.item(row, 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            "Are you sure you want to delete this printer? All components will also be deleted.\n\n"
            "Note: If this printer is used in any print jobs, it cannot be deleted.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_handler.delete_printer(printer_id)
                self.load_printers()
                self.load_components()
                QMessageBox.information(self, "Success", "Printer deleted successfully!")
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete printer: {str(e)}")
    
    def add_component(self):
        """Add a new component to the selected printer."""
        selected_rows = self.printer_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a printer to add a component to.")
            return
            
        # Get the printer ID from the first column of the selected row
        row = self.printer_table.currentRow()
        printer_id = int(self.printer_table.item(row, 0).text())
        
        # Open component dialog
        dialog = ComponentDialog(self, printer_id)
        if dialog.exec_():
            component_data = dialog.get_data()
            
            try:
                self.db_handler.add_printer_component(
                    printer_id=printer_id,
                    name=component_data['name'],
                    replacement_interval=component_data['interval'],
                    notes=component_data['notes']
                )
                
                # Switch to components tab and refresh
                self.tab_widget.setCurrentIndex(1)
                self.load_components()
                
                QMessageBox.information(self, "Success", "Component added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add component: {str(e)}")
    
    def reset_component_usage(self):
        """Reset the usage hours for a component."""
        selected_rows = self.component_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a component to reset.")
            return
            
        # Get the component ID from the first column of the selected row
        row = self.component_table.currentRow()
        component_id = int(self.component_table.item(row, 0).text())
        
        # Confirm reset
        reply = QMessageBox.question(
            self, 
            "Confirm Reset",
            "Are you sure you want to reset the usage hours to 0?\n"
            "This is typically done after replacing the component.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Update component usage to 0
                # Note: the db_handler method updates hours, not sets them directly,
                # so we'll need to get the current hours and subtract from it
                current_hours = float(self.component_table.item(row, 4).text())
                self.db_handler.update_component_usage(component_id, -current_hours)
                
                self.load_components()
                QMessageBox.information(self, "Success", "Component usage reset to 0 hours!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset component usage: {str(e)}")
    
    def remove_component(self):
        """Remove a component from the database."""
        QMessageBox.information(
            self, 
            "Not Implemented",
            "Component removal is not directly implemented in this version.\n"
            "Components are automatically removed when their associated printer is deleted."
        )