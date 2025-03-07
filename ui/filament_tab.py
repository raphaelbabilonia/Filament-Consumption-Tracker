"""
Filament inventory management tab.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel, 
                             QLineEdit, QDoubleSpinBox, QComboBox, QMessageBox,
                             QHeaderView, QFormLayout, QDateEdit, QTabWidget,
                             QSplitter, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from database.db_handler import DatabaseHandler


class FilamentDialog(QDialog):
    """Dialog for editing filament details."""
    
    def __init__(self, parent=None, filament_data=None):
        """Initialize filament dialog."""
        super().__init__(parent)
        self.filament_data = filament_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Edit Filament")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Quantity remaining
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 100000)
        self.quantity_input.setSuffix(" g")
        if self.filament_data:
            self.quantity_input.setValue(self.filament_data.get('quantity_remaining', 0))
        form_layout.addRow("Quantity Remaining (g):", self.quantity_input)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
        
    def get_data(self):
        """Get the updated data."""
        return {
            'quantity_remaining': self.quantity_input.value(),
        }


class FilamentTab(QWidget):
    """Filament inventory management tab."""
    
    def __init__(self, db_handler):
        """Initialize filament tab."""
        super().__init__()
        
        self.db_handler = db_handler
        self.setup_ui()
        self.load_filaments()
        self.load_aggregated_inventory()
        self.populate_dynamic_dropdowns()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create tabs for individual spools and aggregated view
        self.tabs = QTabWidget()
        
        # Tab for adding new filament and individual spool view
        spools_tab = QWidget()
        spools_layout = QVBoxLayout()
        
        # Create the form for adding new filament
        add_form_box = QGroupBox("Add New Filament")
        form_layout = QFormLayout()
        
        # Filament type
        self.type_combo = QComboBox()
        # We'll populate this from the database instead of hardcoding
        self.type_combo.setEditable(True)
        
        # Disconnect and reconnect type_changed to avoid recursive calls during setup
        self.type_combo.currentTextChanged.disconnect() if self.type_combo.receivers(self.type_combo.currentTextChanged) > 0 else None
        self.type_combo.currentTextChanged.connect(self.type_changed)
        
        form_layout.addRow("Type:", self.type_combo)
        
        # Filament color
        self.color_combo = QComboBox()
        self.color_combo.setEditable(True)
        form_layout.addRow("Color:", self.color_combo)
        
        # Filament brand
        self.brand_combo = QComboBox()
        self.brand_combo.setEditable(True)
        form_layout.addRow("Brand:", self.brand_combo)
        
        # Spool weight
        self.spool_weight_input = QDoubleSpinBox()
        self.spool_weight_input.setRange(0, 10000)
        self.spool_weight_input.setValue(1000)  # Default to 1kg
        self.spool_weight_input.setSuffix(" g")
        form_layout.addRow("Spool Weight:", self.spool_weight_input)
        
        # Remaining quantity
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 10000)
        self.quantity_input.setValue(1000)  # Default to 1kg
        self.quantity_input.setSuffix(" g")
        form_layout.addRow("Quantity Remaining:", self.quantity_input)
        
        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000)
        self.price_input.setValue(25)  # Default price
        self.price_input.setPrefix("$ ")
        form_layout.addRow("Price:", self.price_input)
        
        # Purchase date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("Purchase Date:", self.date_input)
        
        # Add button
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Filament")
        self.add_button.clicked.connect(self.add_filament)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        
        add_form_box.setLayout(form_layout)
        
        # Create table for displaying individual filament spools
        self.filament_table = QTableWidget()
        self.filament_table.setColumnCount(8)
        self.filament_table.setHorizontalHeaderLabels([
            "ID", "Type", "Color", "Brand", "Remaining (g)", 
            "Spool Weight (g)", "Price", "Purchase Date"
        ])
        self.filament_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.filament_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Buttons for editing and deleting filaments
        button_layout2 = QHBoxLayout()
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_filament)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_filament)
        button_layout2.addWidget(self.edit_button)
        button_layout2.addWidget(self.delete_button)
        button_layout2.addStretch()
        
        # Add widgets to spools tab layout
        spools_layout.addWidget(add_form_box)
        spools_layout.addLayout(button_layout)
        spools_layout.addWidget(QLabel("Individual Filament Spools:"))
        spools_layout.addWidget(self.filament_table)
        spools_layout.addLayout(button_layout2)
        
        spools_tab.setLayout(spools_layout)
        
        # Tab for aggregated inventory view
        aggregated_tab = QWidget()
        aggregated_layout = QVBoxLayout()
        
        # Create table for displaying aggregated filament inventory
        self.aggregated_table = QTableWidget()
        self.aggregated_table.setColumnCount(7)
        self.aggregated_table.setHorizontalHeaderLabels([
            "Type", "Color", "Brand", "Total Quantity (g)", 
            "Remaining (g)", "% Remaining", "Spools"
        ])
        self.aggregated_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.aggregated_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Add widgets to aggregated tab layout
        aggregated_layout.addWidget(QLabel("<h3>Aggregated Filament Inventory</h3>"))
        aggregated_layout.addWidget(QLabel("Shows total weight of each filament type/color/brand combination"))
        aggregated_layout.addWidget(self.aggregated_table)
        
        # Refresh button for aggregated view
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Inventory")
        self.refresh_button.clicked.connect(self.load_aggregated_inventory)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_button)
        aggregated_layout.addLayout(refresh_layout)
        
        aggregated_tab.setLayout(aggregated_layout)
        
        # Add tabs to the tab widget
        self.tabs.addTab(spools_tab, "Filament Spools")
        self.tabs.addTab(aggregated_tab, "Aggregated Inventory")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
        
    def populate_dynamic_dropdowns(self):
        """Populate dynamic dropdown menus with existing values."""
        try:
            # Block signals to prevent recursive calls
            self.type_combo.blockSignals(True)
            self.color_combo.blockSignals(True)
            self.brand_combo.blockSignals(True)
            
            # Save current values
            current_type = self.type_combo.currentText()
            current_color = self.color_combo.currentText()
            current_brand = self.brand_combo.currentText()
            
            # Clear existing items
            self.type_combo.clear()
            self.color_combo.clear()
            self.brand_combo.clear()
            
            # Get unique types, colors and brands from the database
            types = self.db_handler.get_filament_types()
            colors = self.db_handler.get_filament_colors()
            brands = self.db_handler.get_filament_brands()
            
            # Add default types if database is empty
            if not types:
                types = ["PLA", "ABS", "PETG", "TPU", "Nylon", "Other"]
            
            # Add to combo boxes
            self.type_combo.addItems(types)
            self.color_combo.addItems(colors)
            self.brand_combo.addItems(brands)
            
            # Restore values if possible
            if current_type in types:
                self.type_combo.setCurrentText(current_type)
            if current_color in colors:
                self.color_combo.setCurrentText(current_color)
            if current_brand in brands:
                self.brand_combo.setCurrentText(current_brand)
            
            # Unblock signals
            self.type_combo.blockSignals(False)
            self.color_combo.blockSignals(False)
            self.brand_combo.blockSignals(False)
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not populate dropdowns: {str(e)}")
    
    def type_changed(self, filament_type):
        """Handle filament type changes to update color and brand options."""
        # This function should only do something if the type affects color/brand options
        # Currently we're just ensuring this doesn't call populate_dynamic_dropdowns to avoid recursion
        pass
        
    def load_filaments(self):
        """Load filaments from database and display in table."""
        try:
            filaments = self.db_handler.get_filaments()
            self.filament_table.setRowCount(len(filaments))
            
            for row, filament in enumerate(filaments):
                # Set ID (hidden)
                id_item = QTableWidgetItem(str(filament.id))
                self.filament_table.setItem(row, 0, id_item)
                
                # Set filament details
                self.filament_table.setItem(row, 1, QTableWidgetItem(filament.type))
                self.filament_table.setItem(row, 2, QTableWidgetItem(filament.color))
                self.filament_table.setItem(row, 3, QTableWidgetItem(filament.brand))
                self.filament_table.setItem(row, 4, QTableWidgetItem(str(filament.quantity_remaining)))
                self.filament_table.setItem(row, 5, QTableWidgetItem(str(filament.spool_weight)))
                
                # Price may be None
                price_text = f"${filament.price:.2f}" if filament.price is not None else "N/A"
                self.filament_table.setItem(row, 6, QTableWidgetItem(price_text))
                
                # Format date
                date_str = filament.purchase_date.strftime("%Y-%m-%d") if filament.purchase_date else "N/A"
                self.filament_table.setItem(row, 7, QTableWidgetItem(date_str))
                
                # Color code low filament quantities
                if filament.quantity_remaining / filament.spool_weight < 0.2:  # Less than 20% remaining
                    for col in range(1, 8):
                        item = self.filament_table.item(row, col)
                        item.setBackground(QColor(255, 200, 200))  # Light red
                
            # Update dropdowns with current values
            self.populate_dynamic_dropdowns()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load filaments: {str(e)}")
    
    def load_aggregated_inventory(self):
        """Load aggregated filament inventory from database."""
        try:
            inventory = self.db_handler.get_aggregated_filament_inventory()
            self.aggregated_table.setRowCount(len(inventory))
            
            for row, item in enumerate(inventory):
                # Set filament details
                self.aggregated_table.setItem(row, 0, QTableWidgetItem(item['type']))
                self.aggregated_table.setItem(row, 1, QTableWidgetItem(item['color']))
                self.aggregated_table.setItem(row, 2, QTableWidgetItem(item['brand']))
                
                # Set quantities
                self.aggregated_table.setItem(row, 3, QTableWidgetItem(f"{item['total_quantity']:.1f}"))
                self.aggregated_table.setItem(row, 4, QTableWidgetItem(f"{item['quantity_remaining']:.1f}"))
                self.aggregated_table.setItem(row, 5, QTableWidgetItem(f"{item['percentage_remaining']:.1f}%"))
                
                # Set spool count
                self.aggregated_table.setItem(row, 6, QTableWidgetItem(str(item['spool_count'])))
                
                # Color code low filament quantities
                if item['percentage_remaining'] < 20:  # Less than 20% remaining
                    for col in range(7):
                        self.aggregated_table.item(row, col).setBackground(QColor(255, 200, 200))  # Light red
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load aggregated inventory: {str(e)}")
    
    def add_filament(self):
        """Add a new filament to inventory."""
        try:
            filament_type = self.type_combo.currentText()
            color = self.color_combo.currentText()
            brand = self.brand_combo.currentText()
            spool_weight = self.spool_weight_input.value()
            quantity = self.quantity_input.value()
            price = self.price_input.value()
            
            # Basic validation
            if not filament_type or not color or not brand:
                QMessageBox.warning(self, "Validation Error", "Type, color, and brand are required fields.")
                return
                
            # Add to database
            self.db_handler.add_filament(
                filament_type=filament_type,
                color=color,
                brand=brand,
                spool_weight=spool_weight,
                quantity_remaining=quantity,
                price=price
            )
            
            # Clear inputs
            self.color_combo.clearEditText()
            self.brand_combo.clearEditText()
            self.spool_weight_input.setValue(1000)
            self.quantity_input.setValue(1000)
            self.price_input.setValue(25)
            
            # Reload tables and dynamic dropdowns
            self.load_filaments()
            self.load_aggregated_inventory()
            self.populate_dynamic_dropdowns()  # This will refresh all dropdowns including types
            
            QMessageBox.information(self, "Success", "Filament added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add filament: {str(e)}")
    
    def edit_filament(self):
        """Edit the selected filament."""
        selected_rows = self.filament_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a filament to edit.")
            return
            
        # Get the filament ID from the first column of the selected row
        row = self.filament_table.currentRow()
        filament_id = int(self.filament_table.item(row, 0).text())
        
        try:
            # Get current data
            current_quantity = float(self.filament_table.item(row, 4).text())
            
            # Prepare data for dialog
            filament_data = {
                'quantity_remaining': current_quantity
            }
            
            # Open edit dialog
            dialog = FilamentDialog(self, filament_data)
            if dialog.exec_():
                updated_data = dialog.get_data()
                self.db_handler.update_filament_quantity(filament_id, updated_data['quantity_remaining'])
                
                # Reload data
                self.load_filaments()
                self.load_aggregated_inventory()
                
                QMessageBox.information(self, "Success", "Filament quantity updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update filament: {str(e)}")
    
    def delete_filament(self):
        """Delete the selected filament."""
        selected_rows = self.filament_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a filament to delete.")
            return
            
        # Get the filament ID from the first column of the selected row
        row = self.filament_table.currentRow()
        filament_id = int(self.filament_table.item(row, 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            "Are you sure you want to delete this filament? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_handler.delete_filament(filament_id)
                
                # Reload data
                self.load_filaments()
                self.load_aggregated_inventory()
                self.populate_dynamic_dropdowns()
                
                QMessageBox.information(self, "Success", "Filament deleted successfully!")
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete filament: {str(e)}")

# Need to import this for the edit_filament method
from PyQt5.QtWidgets import QInputDialog