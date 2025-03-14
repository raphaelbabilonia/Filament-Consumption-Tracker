"""
Printer management tab interface.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel, 
                             QLineEdit, QTextEdit, QMessageBox, QInputDialog,
                             QHeaderView, QFormLayout, QDateEdit, QTabWidget,
                             QSpinBox, QDoubleSpinBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

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


class PrinterDialog(QDialog):
    """Dialog for adding or editing printer details."""
    
    def __init__(self, parent=None, printer_data=None):
        """Initialize printer dialog."""
        super().__init__(parent)
        self.printer_data = printer_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        if self.printer_data:
            self.setWindowTitle("Edit Printer")
        else:
            self.setWindowTitle("Add Printer")
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Printer name
        self.name_input = QLineEdit()
        if self.printer_data and 'name' in self.printer_data:
            self.name_input.setText(self.printer_data.get('name', ''))
        form_layout.addRow("Name:", self.name_input)
        
        # Printer model
        self.model_input = QLineEdit()
        if self.printer_data and 'model' in self.printer_data:
            self.model_input.setText(self.printer_data.get('model', ''))
        form_layout.addRow("Model:", self.model_input)
        
        # Power consumption
        self.power_consumption_input = QDoubleSpinBox()
        self.power_consumption_input.setRange(0.0, 1000.0)
        self.power_consumption_input.setDecimals(2)
        self.power_consumption_input.setSuffix(" kWh")
        if self.printer_data and 'power_consumption' in self.printer_data:
            self.power_consumption_input.setValue(self.printer_data.get('power_consumption', 0.0))
        else:
            self.power_consumption_input.setValue(0.0)
        form_layout.addRow("Power Consumption (kWh):", self.power_consumption_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        if self.printer_data and 'notes' in self.printer_data:
            self.notes_input.setPlainText(self.printer_data.get('notes', ''))
        form_layout.addRow("Notes:", self.notes_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def get_data(self):
        """Get the printer data from the form."""
        return {
            'name': self.name_input.text().strip(),
            'model': self.model_input.text().strip(),
            'power_consumption': self.power_consumption_input.value(),
            'notes': self.notes_input.toPlainText().strip()
        }


class PrinterTab(QWidget):
    """Printer management tab."""
    
    printer_updated = pyqtSignal()
    
    def __init__(self, db_handler):
        """Initialize printer tab."""
        super().__init__()
        
        self.db_handler = db_handler
        
        # Track modified items
        self.modified_printers = set()
        self.modified_components = set()
        
        # Track orientation state
        self.is_portrait = False
        
        self.setup_ui()
        self.load_printers()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create tabs for printers and components
        self.tab_widget = QTabWidget()
        
        # Printers tab
        printers_widget = QWidget()
        printers_layout = QVBoxLayout()
        
        # Add button
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Printer")
        self.add_button.clicked.connect(self.add_printer)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        
        # Create table for displaying printers
        self.printer_table = QTableWidget()
        self.printer_table.setColumnCount(5)
        self.printer_table.setHorizontalHeaderLabels([
            "ID", "Name", "Model", "Power (kWh)", "Notes"
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
        self.electricity_cost_button = QPushButton("Set Electricity Cost")
        self.electricity_cost_button.clicked.connect(self.set_electricity_cost)
        
        button_layout2.addWidget(self.edit_button)
        button_layout2.addWidget(self.delete_button)
        button_layout2.addStretch()
        button_layout2.addWidget(self.electricity_cost_button)
        button_layout2.addWidget(self.add_component_button)
        
        # Add widgets to printers layout
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
        """Load printers from the database and display in the table."""
        try:
            printers = self.db_handler.get_printers()
            self.printer_table.setRowCount(len(printers))
            
            for row, printer in enumerate(printers):
                self.printer_table.setItem(row, 0, QTableWidgetItem(str(printer.id)))
                self.printer_table.setItem(row, 1, QTableWidgetItem(printer.name))
                self.printer_table.setItem(row, 2, QTableWidgetItem(printer.model or ""))
                self.printer_table.setItem(row, 3, QTableWidgetItem(f"{printer.power_consumption:.2f}"))
                self.printer_table.setItem(row, 4, QTableWidgetItem(printer.notes or ""))
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
        # Create and show the dialog
        dialog = PrinterDialog(self)
        result = dialog.exec_()
        
        if result != QDialog.Accepted:
            return
            
        printer_data = dialog.get_data()
        
        # Basic validation
        if not printer_data['name']:
            QMessageBox.warning(self, "Missing Information", "Please enter a printer name.")
            return
            
        try:
            self.db_handler.add_printer(
                name=printer_data['name'],
                model=printer_data['model'],
                power_consumption=printer_data['power_consumption'],
                notes=printer_data['notes']
            )
            
            # Refresh the printer list
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
        current_power = float(self.printer_table.item(row, 3).text())
        current_notes = self.printer_table.item(row, 4).text()
        
        # Create printer data dictionary
        printer_data = {
            'name': current_name,
            'model': current_model,
            'power_consumption': current_power,
            'notes': current_notes
        }
        
        # Create and show the dialog
        dialog = PrinterDialog(self, printer_data)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            updated_data = dialog.get_data()
            
            try:
                self.db_handler.update_printer(
                    printer_id=printer_id,
                    name=updated_data['name'],
                    model=updated_data['model'],
                    power_consumption=updated_data['power_consumption'],
                    notes=updated_data['notes']
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
        """Remove a selected component from the database."""
        selected_items = self.component_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a component to remove.")
            return
            
        row = selected_items[0].row()
        component_id = int(self.component_table.item(row, 0).text())
        component_name = self.component_table.item(row, 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Removal",
            f"Are you sure you want to remove the component '{component_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove component from database
            self.db_handler.remove_component(component_id)
            
            # Refresh component list
            self.load_components()
            
            QMessageBox.information(
                self,
                "Component Removed",
                f"Component '{component_name}' has been removed from the database.",
                QMessageBox.Ok
            )
    
    def set_electricity_cost(self):
        """Set the global electricity cost per kWh."""
        # Get current electricity cost
        current_cost = self.db_handler.get_electricity_cost()
        
        # Create dialog for setting electricity cost
        electricity_cost_dialog = QDialog(self)
        electricity_cost_dialog.setWindowTitle("Set Electricity Cost per kWh")
        electricity_cost_dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Electricity cost per kWh input
        cost_input = QDoubleSpinBox()
        cost_input.setRange(0.01, 10.0)
        cost_input.setDecimals(2)
        cost_input.setValue(current_cost)
        cost_input.setSingleStep(0.01)
        cost_input.setSuffix(" $/kWh")
        form_layout.addRow("Electricity Cost per kWh:", cost_input)
        
        # Information label
        info_label = QLabel("This setting will be used for all electricity cost calculations throughout the application.")
        info_label.setWordWrap(True)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(electricity_cost_dialog.accept)
        button_box.rejected.connect(electricity_cost_dialog.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(info_label)
        layout.addWidget(button_box)
        
        electricity_cost_dialog.setLayout(layout)
        
        # Show dialog and process result
        if electricity_cost_dialog.exec_():
            new_cost = cost_input.value()
            # Save to database
            self.db_handler.set_electricity_cost(new_cost)
            QMessageBox.information(
                self,
                "Electricity Cost Updated",
                f"Electricity cost per kWh has been set to ${new_cost:.2f}.\n\n"
                "This value will be used for all electricity cost calculations in the application.",
                QMessageBox.Ok
            )

    def connect_signals(self):
        """Connect signals to handle table cell changes."""
        self.printer_table.cellChanged.connect(self.on_printer_cell_changed)
        self.component_table.cellChanged.connect(self.on_component_cell_changed)

    def on_printer_cell_changed(self, row, column):
        """Handle printer table cell changes."""
        if column > 0:  # Ignore ID column
            printer_id = self.printer_table.item(row, 0).data(Qt.UserRole)
            if printer_id:
                self.modified_printers.add(printer_id)
                # Set printer name in bold to indicate unsaved changes
                name_item = self.printer_table.item(row, 1)
                if name_item:
                    font = name_item.font()
                    font.setBold(True)
                    name_item.setFont(font)

    def on_component_cell_changed(self, row, column):
        """Handle component table cell changes."""
        if column > 0:  # Ignore ID column
            component_id = self.component_table.item(row, 0).data(Qt.UserRole)
            if component_id:
                self.modified_components.add(component_id)
                # Set component name in bold to indicate unsaved changes
                name_item = self.component_table.item(row, 1)
                if name_item:
                    font = name_item.font()
                    font.setBold(True)
                    name_item.setFont(font)

    def has_unsaved_changes(self):
        """Check if there are any unsaved changes in the printer tab."""
        return (len(self.modified_printers) > 0 or 
                len(self.modified_components) > 0)
    
    def save_all_changes(self):
        """Save all pending changes in the printer tab."""
        # Since we don't have direct save methods for each table,
        # we'll simply reload the data and emit the signal to indicate changes
        
        # Reload the data to refresh the views
        self.load_printers()
        
        # Clear modification tracking
        self.modified_printers.clear()
        self.modified_components.clear()
        
        # Emit signal to notify that printer data has been updated
        self.printer_updated.emit()

    def adjust_for_portrait(self, is_portrait):
        """Adjust the layout based on screen orientation."""
        self.is_portrait = is_portrait
        
        if is_portrait:
            # Vertical monitor adjustments
            
            # Optimize printer table column widths for narrower display
            if hasattr(self, 'printer_table'):
                header = self.printer_table.horizontalHeader()
                header.resizeSections(QHeaderView.ResizeToContents)
                
                # Make specific columns fixed width and narrower
                for col_idx, col_width in [
                    (0, 40),     # ID column
                    (1, 140),    # Name column
                    (2, 120),    # Make column
                    (3, 100),    # Model column
                    (4, 60),     # Power column
                    (5, 60)      # Date column
                ]:
                    if col_idx < self.printer_table.columnCount():
                        header.setSectionResizeMode(col_idx, QHeaderView.Fixed)
                        header.resizeSection(col_idx, col_width)
            
            # Adjust form layout if needed
            if hasattr(self, 'form_layout'):
                # Reduce spacing in form layout
                self.form_layout.setVerticalSpacing(5)
                self.form_layout.setHorizontalSpacing(5)
        else:
            # Reset to landscape mode (horizontal monitor)
            
            # Reset table columns to default interactive mode
            if hasattr(self, 'printer_table'):
                header = self.printer_table.horizontalHeader()
                for i in range(self.printer_table.columnCount()):
                    header.setSectionResizeMode(i, QHeaderView.Interactive)
                header.resizeSections(QHeaderView.ResizeToContents)
            
            # Reset form layout spacing if needed
            if hasattr(self, 'form_layout'):
                self.form_layout.setVerticalSpacing(10)
                self.form_layout.setHorizontalSpacing(10)