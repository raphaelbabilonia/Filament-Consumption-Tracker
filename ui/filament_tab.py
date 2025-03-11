"""
Filament inventory management tab.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel, 
                             QLineEdit, QDoubleSpinBox, QComboBox, QMessageBox,
                             QHeaderView, QFormLayout, QDateEdit, QTabWidget,
                             QSplitter, QDialog, QDialogButtonBox, QInputDialog,
                             QListWidget, QListWidgetItem, QPlainTextEdit, QCheckBox,
                             QMenu, QAction, QScrollArea)
from PyQt5.QtCore import Qt, QDate, QSortFilterProxyModel, QTimer
from PyQt5.QtGui import QColor, QCursor

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
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        if self.filament_data and 'type' in self.filament_data:
            self.type_combo.addItem(self.filament_data.get('type', ''))
            self.type_combo.setCurrentText(self.filament_data.get('type', ''))
        form_layout.addRow("Type:", self.type_combo)
        
        # Color
        self.color_combo = QComboBox()
        self.color_combo.setEditable(True)
        if self.filament_data and 'color' in self.filament_data:
            self.color_combo.addItem(self.filament_data.get('color', ''))
            self.color_combo.setCurrentText(self.filament_data.get('color', ''))
        form_layout.addRow("Color:", self.color_combo)
        
        # Brand
        self.brand_combo = QComboBox()
        self.brand_combo.setEditable(True)
        if self.filament_data and 'brand' in self.filament_data:
            self.brand_combo.addItem(self.filament_data.get('brand', ''))
            self.brand_combo.setCurrentText(self.filament_data.get('brand', ''))
        form_layout.addRow("Brand:", self.brand_combo)
        
        # Quantity remaining
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 100000)
        self.quantity_input.setSuffix(" g")
        if self.filament_data and 'quantity_remaining' in self.filament_data:
            self.quantity_input.setValue(self.filament_data.get('quantity_remaining', 0))
        form_layout.addRow("Quantity Remaining (g):", self.quantity_input)
        
        # Spool weight
        self.spool_weight_input = QDoubleSpinBox()
        self.spool_weight_input.setRange(0, 100000)
        self.spool_weight_input.setSuffix(" g")
        if self.filament_data and 'spool_weight' in self.filament_data:
            self.spool_weight_input.setValue(self.filament_data.get('spool_weight', 0))
        form_layout.addRow("Spool Weight (g):", self.spool_weight_input)
        
        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000)
        self.price_input.setPrefix("$ ")
        if self.filament_data and 'price' in self.filament_data:
            self.price_input.setValue(self.filament_data.get('price', 0))
        form_layout.addRow("Price:", self.price_input)
        
        # Purchase date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if self.filament_data and 'purchase_date' in self.filament_data:
            self.date_input.setDate(self.filament_data.get('purchase_date', QDate.currentDate()))
        else:
            self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Purchase Date:", self.date_input)
        
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
            'type': self.type_combo.currentText(),
            'color': self.color_combo.currentText(),
            'brand': self.brand_combo.currentText(),
            'quantity_remaining': self.quantity_input.value(),
            'spool_weight': self.spool_weight_input.value(),
            'price': self.price_input.value(),
            'purchase_date': self.date_input.date().toPyDate()
        }


class FilamentLinkGroupDialog(QDialog):
    """Dialog for creating and managing filament link groups."""
    
    def __init__(self, parent=None, db_handler=None, group_id=None):
        """Initialize the dialog."""
        super().__init__(parent)
        self.db_handler = db_handler
        self.group_id = group_id
        self.group_data = None
        self.preserved_ideal_quantities = {}
        
        # Load group data if editing an existing group
        if group_id:
            self.group_data = self.db_handler.get_filament_link_group(group_id)
            if not self.group_data:
                QMessageBox.warning(self, "Error", f"Group with ID {group_id} not found")
                self.reject()
                return
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        if self.group_id:
            self.setWindowTitle("Edit Filament Link Group")
        else:
            self.setWindowTitle("Create Filament Link Group")
            
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Group information
        form_layout = QFormLayout()
        
        # Name field
        self.name_input = QLineEdit()
        if self.group_data:
            self.name_input.setText(self.group_data.name)
        form_layout.addRow("Group Name:", self.name_input)
        
        # Description field
        self.description_input = QPlainTextEdit()
        if self.group_data and self.group_data.description:
            self.description_input.setPlainText(self.group_data.description)
        form_layout.addRow("Description:", self.description_input)
        
        # Ideal quantity
        self.ideal_qty_input = QDoubleSpinBox()
        self.ideal_qty_input.setRange(0, 100000)
        self.ideal_qty_input.setSuffix(" g")
        if self.group_data:
            self.ideal_qty_input.setValue(self.group_data.ideal_quantity)
        form_layout.addRow("Ideal Quantity (g):", self.ideal_qty_input)
        
        # Add the form to the layout
        layout.addLayout(form_layout)
        
        # Linked filaments section (only for editing existing groups)
        if self.group_id:
            group_box = QGroupBox("Linked Filaments")
            group_layout = QVBoxLayout()
            
            # List of currently linked filaments
            self.linked_filaments_list = QListWidget()
            self.load_linked_filaments()
            group_layout.addWidget(self.linked_filaments_list)
            
            # Buttons for managing linked filaments
            buttons_layout = QHBoxLayout()
            self.add_filament_button = QPushButton("Add Filament")
            self.add_filament_button.clicked.connect(self.add_filament)
            self.remove_filament_button = QPushButton("Remove Selected")
            self.remove_filament_button.clicked.connect(self.remove_filament)
            
            buttons_layout.addWidget(self.add_filament_button)
            buttons_layout.addWidget(self.remove_filament_button)
            
            group_layout.addLayout(buttons_layout)
            group_box.setLayout(group_layout)
            layout.addWidget(group_box)
            
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        
    def load_linked_filaments(self):
        """Load the current linked filaments into the list."""
        self.linked_filaments_list.clear()
        
        if self.group_data and self.group_data.filament_links:
            for link in self.group_data.filament_links:
                item_text = f"{link.type} - {link.color} - {link.brand}"
                list_item = QListWidgetItem(item_text)
                # Store filament data in item
                list_item.setData(Qt.UserRole, {
                    'type': link.type,
                    'color': link.color,
                    'brand': link.brand
                })
                self.linked_filaments_list.addItem(list_item)
    
    def add_filament(self):
        """Add a filament to the link group."""
        # Store current ideal quantities to preserve them
        preserved_ideal_quantities = {}
        
        # Get the parent FilamentTab instance to access the status table
        parent_tab = None
        parent = self.parent()
        while parent:
            if isinstance(parent, FilamentTab):
                parent_tab = parent
                break
            parent = parent.parent()
        
        # If we found the parent tab, collect current ideal quantities
        if parent_tab and hasattr(parent_tab, 'status_table'):
            for row in range(parent_tab.status_table.rowCount()):
                # Skip if any items are missing
                if any(parent_tab.status_table.item(row, col) is None for col in [0, 1, 2, 4]):
                    continue
                
                # Get filament details
                type_item = parent_tab.status_table.item(row, 0)
                if type_item.font().bold():  # Skip group entries
                    continue
                    
                type_val = type_item.text()
                color_val = parent_tab.status_table.item(row, 1).text()
                brand_val = parent_tab.status_table.item(row, 2).text()
                
                # Get ideal quantity
                ideal_qty_item = parent_tab.status_table.item(row, 4)
                try:
                    ideal_qty = float(ideal_qty_item.text())
                    if ideal_qty > 0:  # Only preserve non-zero values
                        preserved_ideal_quantities[(type_val, color_val, brand_val)] = ideal_qty
                except (ValueError, TypeError):
                    pass
        
        # Get available filaments from the database
        filaments = self.db_handler.get_filaments()
        
        # Create a list of available filaments that aren't already in the group
        available_filaments = []
        
        # Get currently linked filament keys
        linked_keys = set()
        if self.group_data and self.group_data.filament_links:
            for link in self.group_data.filament_links:
                linked_keys.add((link.type, link.color, link.brand))
        
        # Track unique filament combinations to prevent duplicates
        unique_filaments = set()
        
        # Add filaments that aren't already linked
        for filament in filaments:
            key = (filament.type, filament.color, filament.brand)
            
            # Skip if already linked or already in our list (prevent duplicates)
            if key in linked_keys or key in unique_filaments:
                continue
                
            # Add to tracking set
            unique_filaments.add(key)
            
            # Add to available filaments list
            available_filaments.append({
                'text': f"{filament.type} - {filament.color} - {filament.brand}",
                'data': {
                    'type': filament.type,
                    'color': filament.color,
                    'brand': filament.brand
                }
            })
        
        if not available_filaments:
            QMessageBox.information(self, "No Filaments", "No additional filaments available to link.")
            return
        
        # Create a dialog with a search box and checkboxes for filaments
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Filaments to Link")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        dialog_layout = QVBoxLayout()
        
        # Add a search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_input = QLineEdit()
        search_input.setPlaceholderText("Type to filter filaments...")
        search_layout.addWidget(search_input)
        dialog_layout.addLayout(search_layout)
        
        # Add a label
        dialog_layout.addWidget(QLabel("Select filaments to add to this group:"))
        
        # Create a scroll area with checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Sort filaments by type, color, brand for easier navigation
        available_filaments.sort(key=lambda f: (f['data']['type'], f['data']['color'], f['data']['brand']))
        
        # Add checkboxes for each filament
        checkboxes = []
        for filament in available_filaments:
            checkbox = QCheckBox(filament['text'])
            checkbox.setProperty('filament_data', filament['data'])
            checkbox.setProperty('search_text', filament['text'].lower())  # For searching
            checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
            
        # Add stretch at the end to keep checkboxes at the top
        scroll_layout.addStretch()
        
        # Set the layout for the scroll content
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        
        # Connect search box to filter function
        def filter_filaments():
            search_text = search_input.text().lower()
            for checkbox in checkboxes:
                checkbox_text = checkbox.property('search_text')
                checkbox.setVisible(search_text in checkbox_text)
        
        search_input.textChanged.connect(filter_filaments)
        
        # Add the scroll area to the dialog
        dialog_layout.addWidget(scroll_area)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        dialog.setLayout(dialog_layout)
        
        # Show the dialog
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Add the selected filaments to the group
            added = False
            for checkbox in checkboxes:
                if checkbox.isChecked():
                    filament_data = checkbox.property('filament_data')
                    try:
                        self.db_handler.add_filament_to_link_group(
                            self.group_id,
                            filament_data['type'],
                            filament_data['color'],
                            filament_data['brand']
                        )
                        added = True
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to add filament: {str(e)}")
            
            # Only reload if filaments were actually added
            if added:
                # Reload the group data and update the list
                self.group_data = self.db_handler.get_filament_link_group(self.group_id)
                self.load_linked_filaments()
                
                # Save the preserved ideal quantities for other code to use
                self.preserved_ideal_quantities = preserved_ideal_quantities
    
    def remove_filament(self):
        """Remove a filament from the link group."""
        selected_items = self.linked_filaments_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a filament to remove.")
            return
        
        # Ask for confirmation
        result = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove the selected filament(s) from this group?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            for item in selected_items:
                filament_data = item.data(Qt.UserRole)
                try:
                    self.db_handler.remove_filament_from_link_group(
                        self.group_id,
                        filament_data['type'],
                        filament_data['color'],
                        filament_data['brand']
                    )
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to remove filament: {str(e)}")
            
            # Reload the group data and update the list
            self.group_data = self.db_handler.get_filament_link_group(self.group_id)
            self.load_linked_filaments()
    
    def accept(self):
        """Save the group data and close the dialog."""
        # Validate inputs
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Group name is required.")
            return
        
        description = self.description_input.toPlainText().strip()
        ideal_qty = self.ideal_qty_input.value()
        
        try:
            if self.group_id:
                # Update existing group
                self.db_handler.update_filament_link_group(
                    self.group_id,
                    name=name,
                    description=description,
                    ideal_quantity=ideal_qty
                )
            else:
                # Create new group
                self.group_id = self.db_handler.create_filament_link_group(
                    name=name,
                    description=description,
                    ideal_quantity=ideal_qty
                )
            
            # Store result data where the parent can access it
            self.result_data = {
                'group_id': self.group_id,
                'preserved_ideal_quantities': self.preserved_ideal_quantities
            }
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save group: {str(e)}")


class FilamentTab(QWidget):
    """Filament inventory management tab."""
    
    def __init__(self, db_handler):
        """Initialize filament tab."""
        super().__init__()
        
        self.db_handler = db_handler
        self.setup_ui()
        self.load_filaments()
        self.load_aggregated_inventory()
        self.load_inventory_status()  # Load inventory status comparison
        self.populate_dynamic_dropdowns()
        
        # Add a timer to refresh the inventory status once on startup
        # This ensures all colors are properly loaded after initialization
        QTimer.singleShot(100, self.check_tpu_transparent)
    
    def check_tpu_transparent(self):
        """Check and repair any filaments with zero ideal quantities."""
        # Since the general solution now handles all filaments, this method just ensures
        # all filaments have their ideal quantities preserved
        print("Running filament quantity check...")
        # Get all ideal quantities from the database to ensure they're preserved
        ideal_quantities = self.capture_current_ideal_quantities()
        self.fix_zero_ideal_quantities(ideal_quantities)
    
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
        
        # Search bar for filament table
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_input.textChanged.connect(self.filter_filament_table)
        search_layout.addWidget(self.search_input)
        
        # Search filter criteria
        search_layout.addWidget(QLabel("Filter by:"))
        self.search_filter_combo = QComboBox()
        self.search_filter_combo.addItems(["All", "Type", "Color", "Brand"])
        self.search_filter_combo.currentTextChanged.connect(self.filter_filament_table)
        search_layout.addWidget(self.search_filter_combo)
        
        # Create table for displaying individual filament spools
        self.filament_table = QTableWidget()
        self.filament_table.setColumnCount(8)
        self.filament_table.setHorizontalHeaderLabels([
            "ID", "Type", "Color", "Brand", "Remaining (g)", 
            "Spool Weight (g)", "Price", "Purchase Date"
        ])
        
        # Enable sorting for filament table
        self.filament_table.setSortingEnabled(True)
        self.filament_table.horizontalHeader().setSectionsClickable(True)
        self.filament_table.horizontalHeader().sectionClicked.connect(self.sort_filament_table)
        
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
        spools_layout.addLayout(search_layout)
        spools_layout.addWidget(self.filament_table)
        spools_layout.addLayout(button_layout2)
        
        spools_tab.setLayout(spools_layout)
        
        # Tab for aggregated inventory view
        aggregated_tab = QWidget()
        aggregated_layout = QVBoxLayout()
        
        # Add widgets to aggregated tab layout
        aggregated_layout.addWidget(QLabel("<h3>Aggregated Filament Inventory</h3>"))
        aggregated_layout.addWidget(QLabel("Shows total weight of each filament type/color/brand combination"))
        
        # Search bar for aggregated table
        search_layout_agg = QHBoxLayout()
        search_layout_agg.addWidget(QLabel("Search:"))
        self.search_input_agg = QLineEdit()
        self.search_input_agg.setPlaceholderText("Enter search term...")
        self.search_input_agg.textChanged.connect(self.filter_aggregated_table)
        search_layout_agg.addWidget(self.search_input_agg)
        
        # Search filter criteria
        search_layout_agg.addWidget(QLabel("Filter by:"))
        self.search_filter_combo_agg = QComboBox()
        self.search_filter_combo_agg.addItems(["All", "Type", "Color", "Brand"])
        self.search_filter_combo_agg.currentTextChanged.connect(self.filter_aggregated_table)
        search_layout_agg.addWidget(self.search_filter_combo_agg)
        
        aggregated_layout.addLayout(search_layout_agg)
        
        # Create table for displaying aggregated filament inventory
        self.aggregated_table = QTableWidget()
        self.aggregated_table.setColumnCount(7)
        self.aggregated_table.setHorizontalHeaderLabels([
            "Type", "Color", "Brand", "Total Quantity (g)", 
            "Remaining (g)", "% Remaining", "Spools"
        ])
        
        # Enable sorting for aggregated table
        self.aggregated_table.setSortingEnabled(True)
        self.aggregated_table.horizontalHeader().setSectionsClickable(True)
        self.aggregated_table.horizontalHeader().sectionClicked.connect(self.sort_aggregated_table)
        
        self.aggregated_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.aggregated_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        aggregated_layout.addWidget(self.aggregated_table)
        
        # Button for setting ideal quantity
        button_layout_agg = QHBoxLayout()
        
        # Refresh button for aggregated view
        self.refresh_button = QPushButton("Refresh Inventory")
        self.refresh_button.clicked.connect(self.load_aggregated_inventory)
        button_layout_agg.addStretch()
        button_layout_agg.addWidget(self.refresh_button)
        
        aggregated_layout.addLayout(button_layout_agg)
        
        aggregated_tab.setLayout(aggregated_layout)
        
        # Tab for inventory status (comparing current vs ideal)
        status_tab = QWidget()
        status_layout = QVBoxLayout()
        
        # Add widgets to status tab layout
        status_layout.addWidget(QLabel("<h3>Inventory Status</h3>"))
        status_layout.addWidget(QLabel("Compare current inventory with ideal quantities"))
        
        # Search bar for status table
        search_layout_status = QHBoxLayout()
        search_layout_status.addWidget(QLabel("Search:"))
        self.search_input_status = QLineEdit()
        self.search_input_status.setPlaceholderText("Enter search term...")
        self.search_input_status.textChanged.connect(self.filter_status_table)
        search_layout_status.addWidget(self.search_input_status)
        
        # Search filter criteria
        search_layout_status.addWidget(QLabel("Filter by:"))
        self.search_filter_combo_status = QComboBox()
        self.search_filter_combo_status.addItems(["All", "Type", "Color", "Brand"])
        self.search_filter_combo_status.currentTextChanged.connect(self.filter_status_table)
        search_layout_status.addWidget(self.search_filter_combo_status)
        
        status_layout.addLayout(search_layout_status)
        
        # Create table for displaying inventory status
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(7)
        self.status_table.setHorizontalHeaderLabels([
            "Type", "Color", "Brand", "Current (g)", 
            "Ideal (g)", "Difference (g)", "Status"
        ])
        
        # Enable sorting for status table
        self.status_table.setSortingEnabled(True)
        self.status_table.horizontalHeader().setSectionsClickable(True)
        self.status_table.horizontalHeader().sectionClicked.connect(self.sort_status_table)
        
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        status_layout.addWidget(self.status_table)
        
        # Button to refresh inventory status
        refresh_status_layout = QHBoxLayout()
        
        # Add Set Ideal Quantity button to Status tab
        self.set_ideal_button = QPushButton("Set Ideal Quantity")
        self.set_ideal_button.clicked.connect(self.set_ideal_quantity)
        refresh_status_layout.addWidget(self.set_ideal_button)
        
        # Add Manage Link Groups button
        self.manage_links_button = QPushButton("Manage Filament Links")
        self.manage_links_button.clicked.connect(self.manage_filament_links)
        refresh_status_layout.addWidget(self.manage_links_button)
        
        refresh_status_layout.addStretch()
        
        self.refresh_status_button = QPushButton("Refresh Status")
        self.refresh_status_button.clicked.connect(self.refresh_inventory_status)
        refresh_status_layout.addWidget(self.refresh_status_button)
        
        status_layout.addLayout(refresh_status_layout)
        
        status_tab.setLayout(status_layout)
        
        # Add tabs to the tab widget
        self.tabs.addTab(spools_tab, "Filament Spools")
        self.tabs.addTab(aggregated_tab, "Aggregated Inventory")
        self.tabs.addTab(status_tab, "Inventory Status")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
        
    def sort_filament_table(self, column_index):
        """Sort the filament table by the specified column."""
        # Toggle between ascending and descending order
        current_order = self.filament_table.horizontalHeader().sortIndicatorOrder()
        if current_order == Qt.AscendingOrder:
            self.filament_table.sortItems(column_index, Qt.DescendingOrder)
        else:
            self.filament_table.sortItems(column_index, Qt.AscendingOrder)
    
    def sort_aggregated_table(self, column_index):
        """Sort the aggregated table by the specified column."""
        # Toggle between ascending and descending order
        current_order = self.aggregated_table.horizontalHeader().sortIndicatorOrder()
        if current_order == Qt.AscendingOrder:
            self.aggregated_table.sortItems(column_index, Qt.DescendingOrder)
        else:
            self.aggregated_table.sortItems(column_index, Qt.AscendingOrder)
        
    def filter_filament_table(self):
        """Filter the filament table based on search input and criteria."""
        search_text = self.search_input.text().lower()
        filter_criteria = self.search_filter_combo.currentText()
        
        for row in range(self.filament_table.rowCount()):
            show_row = False
            
            if filter_criteria == "All" or not search_text:
                # Check all columns except ID (column 0)
                for col in range(1, self.filament_table.columnCount()):
                    item = self.filament_table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break
            else:
                # Map filter criteria to column index
                column_map = {"Type": 1, "Color": 2, "Brand": 3}
                col = column_map.get(filter_criteria, 1)
                item = self.filament_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
            
            self.filament_table.setRowHidden(row, not show_row)
    
    def filter_aggregated_table(self):
        """Filter the aggregated table based on search input and criteria."""
        search_text = self.search_input_agg.text().lower()
        filter_criteria = self.search_filter_combo_agg.currentText()
        
        for row in range(self.aggregated_table.rowCount()):
            show_row = False
            
            if filter_criteria == "All" or not search_text:
                # Check all columns
                for col in range(self.aggregated_table.columnCount()):
                    item = self.aggregated_table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break
            else:
                # Map filter criteria to column index
                column_map = {"Type": 0, "Color": 1, "Brand": 2}
                col = column_map.get(filter_criteria, 0)
                item = self.aggregated_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
            
            self.aggregated_table.setRowHidden(row, not show_row)
        
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
                
                # Use QTableWidgetItem for numerical values to enable proper sorting
                quantity_item = QTableWidgetItem()
                quantity_item.setData(Qt.DisplayRole, filament.quantity_remaining)
                self.filament_table.setItem(row, 4, quantity_item)
                
                spool_weight_item = QTableWidgetItem()
                spool_weight_item.setData(Qt.DisplayRole, filament.spool_weight)
                self.filament_table.setItem(row, 5, spool_weight_item)
                
                # Price may be None
                price_item = QTableWidgetItem()
                if filament.price is not None:
                    price_item.setData(Qt.DisplayRole, filament.price)
                    price_item.setText(f"${filament.price:.2f}")
                else:
                    price_item.setText("N/A")
                self.filament_table.setItem(row, 6, price_item)
                
                # Format date
                date_item = QTableWidgetItem()
                if filament.purchase_date:
                    date_str = filament.purchase_date.strftime("%Y-%m-%d")
                    # Store as ISO format for proper sorting
                    date_item.setData(Qt.UserRole, filament.purchase_date.isoformat())
                    date_item.setText(date_str)
                else:
                    date_item.setText("N/A")
                self.filament_table.setItem(row, 7, date_item)
                
                # Color code filament quantities based on percentage remaining
                remaining_percentage = filament.quantity_remaining / filament.spool_weight * 100
                
                # Improved color coding based on remaining percentage, in 20% increments
                for col in range(1, 8):
                    item = self.filament_table.item(row, col)
                
                    if remaining_percentage > 80:
                        item.setBackground(QColor(200, 255, 200))  # Very Light Green (81-100%)
                    elif remaining_percentage > 60:
                        item.setBackground(QColor(220, 245, 255))  # Very Light Cyan (61-80%)
                    elif remaining_percentage > 40:
                        item.setBackground(QColor(255, 250, 200))  # Very Light Yellow (41-60%)
                    elif remaining_percentage > 20:
                        item.setBackground(QColor(255, 220, 180))  # Very Light Orange (21-40%)
                    else:
                        item.setBackground(QColor(255, 200, 200))  # Very Light Red (0-20%)
                
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
                total_qty_item = QTableWidgetItem()
                total_qty_item.setData(Qt.DisplayRole, item['total_quantity'])
                total_qty_item.setText(f"{item['total_quantity']:.1f}")
                self.aggregated_table.setItem(row, 3, total_qty_item)
                
                remaining_qty_item = QTableWidgetItem()
                remaining_qty_item.setData(Qt.DisplayRole, item['quantity_remaining'])
                remaining_qty_item.setText(f"{item['quantity_remaining']:.1f}")
                self.aggregated_table.setItem(row, 4, remaining_qty_item)
                
                percent_item = QTableWidgetItem()
                percent_item.setData(Qt.DisplayRole, item['percentage_remaining'])
                percent_item.setText(f"{item['percentage_remaining']:.1f}%")
                self.aggregated_table.setItem(row, 5, percent_item)
                
                # Set spool count
                spools_item = QTableWidgetItem()
                spools_item.setData(Qt.DisplayRole, item['spool_count'])
                spools_item.setText(str(item['spool_count']))
                self.aggregated_table.setItem(row, 6, spools_item)
                
                # Color code filament quantities based on percentage remaining
                remaining_percentage = item['quantity_remaining'] / item['total_quantity'] * 100
                
                # Improved color coding based on remaining percentage, in 20% increments
                for col in range(7):
                    item = self.aggregated_table.item(row, col)
                
                    if remaining_percentage > 80:
                        item.setBackground(QColor(200, 255, 200))  # Very Light Green (81-100%)
                    elif remaining_percentage > 60:
                        item.setBackground(QColor(220, 245, 255))  # Very Light Cyan (61-80%)
                    elif remaining_percentage > 40:
                        item.setBackground(QColor(255, 250, 200))  # Very Light Yellow (41-60%)
                    elif remaining_percentage > 20:
                        item.setBackground(QColor(255, 220, 180))  # Very Light Orange (21-40%)
                    else:
                        item.setBackground(QColor(255, 200, 200))  # Very Light Red (0-20%)
                
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
            purchase_date = self.date_input.date().toPyDate()
            
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
                price=price,
                purchase_date=purchase_date
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
            filament_type = self.filament_table.item(row, 1).text()
            color = self.filament_table.item(row, 2).text()
            brand = self.filament_table.item(row, 3).text()
            quantity_remaining = float(self.filament_table.item(row, 4).text())
            spool_weight = float(self.filament_table.item(row, 5).text())
            
            # Get price (may be N/A)
            price_text = self.filament_table.item(row, 6).text()
            price = None
            if price_text != "N/A":
                price = float(price_text.replace('$', ''))
            
            # Get purchase date
            date_text = self.filament_table.item(row, 7).text()
            purchase_date = QDate.currentDate()
            if date_text != "N/A":
                purchase_date = QDate.fromString(date_text, "yyyy-MM-dd")
            
            # Prepare data for dialog
            filament_data = {
                'type': filament_type,
                'color': color,
                'brand': brand,
                'quantity_remaining': quantity_remaining,
                'spool_weight': spool_weight,
                'price': price if price else 0,
                'purchase_date': purchase_date
            }
            
            # Open edit dialog
            dialog = FilamentDialog(self, filament_data)
            
            # Populate dropdown options in the dialog
            dialog.type_combo.addItems(self.db_handler.get_filament_types())
            dialog.color_combo.addItems(self.db_handler.get_filament_colors())
            dialog.brand_combo.addItems(self.db_handler.get_filament_brands())
            
            if dialog.exec_():
                updated_data = dialog.get_data()
                
                # Update filament in database
                self.db_handler.update_filament(
                    filament_id, 
                    updated_data['type'],
                    updated_data['color'], 
                    updated_data['brand'],
                    updated_data['spool_weight'],
                    updated_data['quantity_remaining'],
                    updated_data['price'],
                    updated_data['purchase_date']
                )
                
                # Reload data
                self.load_filaments()
                self.load_aggregated_inventory()
                self.populate_dynamic_dropdowns()
                
                QMessageBox.information(self, "Success", "Filament updated successfully!")
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
    
    def sort_status_table(self, column_index):
        """Sort the inventory status table by the specified column."""
        # Toggle between ascending and descending order
        current_order = self.status_table.horizontalHeader().sortIndicatorOrder()
        if current_order == Qt.AscendingOrder:
            self.status_table.sortItems(column_index, Qt.DescendingOrder)
        else:
            self.status_table.sortItems(column_index, Qt.AscendingOrder)
    
    def filter_status_table(self):
        """Filter the inventory status table based on search input and criteria."""
        search_text = self.search_input_status.text().lower()
        filter_criteria = self.search_filter_combo_status.currentText()
        
        for row in range(self.status_table.rowCount()):
            show_row = False
            
            if filter_criteria == "All" or not search_text:
                # Check all columns
                for col in range(self.status_table.columnCount()):
                    item = self.status_table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break
            else:
                # Map filter criteria to column index
                column_map = {"Type": 0, "Color": 1, "Brand": 2}
                col = column_map.get(filter_criteria, 0)
                item = self.status_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
            
            self.status_table.setRowHidden(row, not show_row)
    
    def set_ideal_quantity(self):
        """Set ideal quantity for selected filament in inventory status view."""
        selected_rows = self.status_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a filament to set ideal quantity.")
            return
        
        # Get current ideal quantities BEFORE making any changes
        current_ideal_quantities = self.capture_current_ideal_quantities()
        
        # Get the selected row
        row = self.status_table.currentRow()
        
        # Get type item to check if it's a group
        type_item = self.status_table.item(row, 0)
        is_group = False
        group_id = None
        
        # Check if it's a linked group
        if type_item.font().bold():
            is_group = True
            group_id = type_item.data(Qt.UserRole)
        
        # Get filament details
        filament_type = type_item.text()
        color = self.status_table.item(row, 1).text()
        brand = self.status_table.item(row, 2).text()
        
        # Current and ideal quantities (for reference)
        current_quantity = float(self.status_table.item(row, 3).text())
        ideal_quantity_text = self.status_table.item(row, 4).text()
        existing_ideal = float(ideal_quantity_text) if ideal_quantity_text else 0
        
        # Prepare dialog text
        if is_group:
            dialog_title = "Set Ideal Quantity for Group"
            dialog_text = f"Enter ideal quantity (in grams) for group: {filament_type}, {color}, {brand}\n"
        else:
            dialog_title = "Set Ideal Quantity"
            dialog_text = f"Enter ideal quantity (in grams) for {filament_type} {color} {brand}:\n"
            
        dialog_text += f"Current quantity: {current_quantity:.1f}g\n"
        dialog_text += f"Current ideal quantity: {existing_ideal:.1f}g"
        
        # Prompt user to enter ideal quantity
        new_ideal_quantity, ok = QInputDialog.getDouble(
            self, 
            dialog_title,
            dialog_text,
            existing_ideal, 0, 100000, 1
        )
        
        if ok:
            try:
                if is_group:
                    # Update the group's ideal quantity
                    self.db_handler.update_filament_link_group(
                        group_id=group_id,
                        ideal_quantity=new_ideal_quantity
                    )
                    print(f"Updated group {group_id} ideal quantity to {new_ideal_quantity}")
                else:
                    # Save ideal quantity in database for individual filament
                    self.db_handler.set_ideal_filament_quantity(
                        filament_type=filament_type,
                        color=color,
                        brand=brand,
                        ideal_quantity=new_ideal_quantity
                    )
                    
                    # Also update our tracking dictionary
                    current_ideal_quantities[(filament_type, color, brand)] = new_ideal_quantity
                    print(f"Set ideal quantity for {filament_type} {color} {brand} to {new_ideal_quantity}")
                
                # Update just the selected row in the table
                if new_ideal_quantity > 0:
                    # Calculate percentage
                    percentage = (current_quantity / new_ideal_quantity) * 100
                    
                    # Update ideal quantity cell
                    ideal_qty_item = self.status_table.item(row, 4)
                    ideal_qty_item.setData(Qt.DisplayRole, new_ideal_quantity)
                    ideal_qty_item.setText(f"{new_ideal_quantity:.1f}")
                    
                    # Update difference cell
                    diff = current_quantity - new_ideal_quantity
                    diff_item = self.status_table.item(row, 5)
                    diff_item.setData(Qt.DisplayRole, diff)
                    diff_item.setText(f"{diff:.1f}")
                    
                    # Update status text
                    status_text = self.get_status_text(percentage)
                    status_item = self.status_table.item(row, 6)
                    status_item.setText(status_text)
                    
                    # Update colors for this row only
                    for col in range(7):
                        table_item = self.status_table.item(row, col)
                        if table_item:
                            self.color_code_status_item(table_item, percentage)
                            
                            # If it's a group, make the color slightly darker
                            if is_group:
                                base_color = table_item.background().color()
                                darker_color = base_color.darker(110)  # 10% darker
                                table_item.setBackground(darker_color)
                else:
                    # If ideal quantity is 0, update to show "No Target Set"
                    percentage = None
                    
                    # Update ideal quantity cell
                    ideal_qty_item = self.status_table.item(row, 4)
                    ideal_qty_item.setData(Qt.DisplayRole, 0)
                    ideal_qty_item.setText("0.0")
                    
                    # Update difference cell
                    diff_item = self.status_table.item(row, 5)
                    diff_item.setData(Qt.DisplayRole, current_quantity)
                    diff_item.setText(f"{current_quantity:.1f}")
                    
                    # Update status text
                    status_item = self.status_table.item(row, 6)
                    status_item.setText("No Target Set")
                    
                    # Update colors for this row only
                    for col in range(7):
                        table_item = self.status_table.item(row, col)
                        if table_item:
                            self.color_code_status_item(table_item, percentage)
                            
                            # If it's a group, make the color slightly darker
                            if is_group:
                                base_color = table_item.background().color()
                                darker_color = base_color.darker(110)  # 10% darker
                                table_item.setBackground(darker_color)
                
                # Instead of refreshing whole table, just verify our database is updated
                # by fetching the ideal quantity directly from database
                actual_db_value = self.db_handler.get_ideal_filament_quantity(filament_type, color, brand)
                if actual_db_value != new_ideal_quantity and not is_group:
                    print(f"Warning: Database ideal quantity ({actual_db_value}) doesn't match set value ({new_ideal_quantity})")
                
                # Ensure the same row remains selected
                if row < self.status_table.rowCount():
                    self.status_table.selectRow(row)
                
                QMessageBox.information(self, "Success", "Ideal quantity set successfully!")
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                QMessageBox.critical(self, "Error", f"Failed to set ideal quantity: {str(e)}\n\nDetails:\n{error_details}")
                # Fall back to full refresh if update fails, using preserved quantities
                self.refresh_inventory_status(current_ideal_quantities)
    
    def refresh_inventory_status(self, preserved_ideal_quantities=None):
        """Refresh the inventory status table and ensure colors are applied properly."""
        # Save current selection if any
        current_row = self.status_table.currentRow()
        current_scroll = self.status_table.verticalScrollBar().value()
        
        # Load the updated inventory status
        try:
            # Capture current ideal quantities if none were provided
            if not preserved_ideal_quantities:
                current_ideal_quantities = self.capture_current_ideal_quantities()
            else:
                current_ideal_quantities = preserved_ideal_quantities
            
            # Get fresh data from database
            inventory_status = self.db_handler.get_inventory_status()
            
            # Create a mapping of current table items for easier updating
            current_items = {}
            
            # Before making any changes, collect information about all current table items
            for row in range(self.status_table.rowCount()):
                # Check for null items
                if self.status_table.item(row, 0) is None:
                    continue
                    
                # Try to identify each row by type/color/brand or group_id
                type_item = self.status_table.item(row, 0)
                color_item = self.status_table.item(row, 1)
                brand_item = self.status_table.item(row, 2)
                ideal_qty_item = self.status_table.item(row, 4)
                
                if type_item is None or color_item is None or brand_item is None or ideal_qty_item is None:
                    continue
                
                is_group = type_item.font().bold()
                
                if is_group and type_item.data(Qt.UserRole) is not None:
                    # Use group ID as key for linked groups
                    group_id = type_item.data(Qt.UserRole)
                    row_key = f"group_{group_id}"
                else:
                    # Use type/color/brand as key for individual filaments
                    type_val = type_item.text()
                    color_val = color_item.text()
                    brand_val = brand_item.text()
                    row_key = f"{type_val}_{color_val}_{brand_val}"
                    
                    # Store ideal quantity for individual filaments (already done in capture_current_ideal_quantities)
                
                # Store information about this row
                current_items[row_key] = {
                    'is_group': is_group,
                    'background_colors': [
                        self.status_table.item(row, col).background() 
                        for col in range(7) if self.status_table.item(row, col) is not None
                    ]
                }
            
            # Apply preserved ideal quantities
            for item in inventory_status:
                if not item.get('is_group', False):
                    key = (item['type'], item['color'], item['brand'])
                    if key in current_ideal_quantities and current_ideal_quantities[key] > 0:
                        # Update the item's ideal quantity to match what was previously set
                        item['ideal_quantity'] = current_ideal_quantities[key]
                        
                        # Recalculate difference and percentage
                        item['difference'] = item['current_quantity'] - item['ideal_quantity']
                        if item['ideal_quantity'] > 0:
                            item['percentage'] = (item['current_quantity'] / item['ideal_quantity'] * 100)
                        else:
                            item['percentage'] = None
            
            # If row count has changed, we need to do a full reload
            if self.status_table.rowCount() != len(inventory_status):
                # Full reload of the table but preserve ideal quantities
                self.load_inventory_status(current_ideal_quantities)
            else:
                # Update in place while preserving existing properties
                for row, item in enumerate(inventory_status):
                    # First, update text values and other data
                    is_group = item.get('is_group', False)
                    
                    # Determine row key
                    if is_group:
                        row_key = f"group_{item.get('group_id')}"
                    else:
                        row_key = f"{item['type']}_{item['color']}_{item['brand']}"
                    
                    # Update current quantity
                    current_qty = item['current_quantity']
                    current_qty_item = self.status_table.item(row, 3)
                    if current_qty_item:
                        current_qty_item.setData(Qt.DisplayRole, current_qty)
                        current_qty_item.setText(f"{current_qty:.1f}")
                    
                    # Update ideal quantity
                    ideal_qty = item['ideal_quantity']
                    ideal_qty_item = self.status_table.item(row, 4)
                    if ideal_qty_item:
                        ideal_qty_item.setData(Qt.DisplayRole, ideal_qty)
                        ideal_qty_item.setText(f"{ideal_qty:.1f}")
                    
                    # Update difference
                    diff = item['difference']
                    diff_item = self.status_table.item(row, 5)
                    if diff_item:
                        diff_item.setData(Qt.DisplayRole, diff)
                        diff_item.setText(f"{diff:.1f}")
                    
                    # Update status text and percentage
                    percentage = item['percentage']
                    status_text = self.get_status_text(percentage)
                    status_item = self.status_table.item(row, 6)
                    if status_item:
                        status_item.setText(status_text)
                    
                    # If we have color information saved for this row, restore it
                    # Otherwise, apply new colors
                    if row_key in current_items:
                        saved_item = current_items[row_key]
                        # Only restore colors if we're not changing from group to non-group or vice versa
                        if saved_item['is_group'] == is_group and saved_item['background_colors']:
                            # Restore saved background colors
                            for col, bg_color in enumerate(saved_item['background_colors']):
                                if col < 7 and self.status_table.item(row, col):
                                    self.status_table.item(row, col).setBackground(bg_color)
                        else:
                            # Apply new colors
                            self._apply_colors_to_row(row, percentage, is_group)
                    else:
                        # Apply new colors
                        self._apply_colors_to_row(row, percentage, is_group)
            
            # Restore selection if possible
            if current_row >= 0 and current_row < self.status_table.rowCount():
                self.status_table.selectRow(current_row)
                
            # Restore scroll position
            self.status_table.verticalScrollBar().setValue(current_scroll)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error refreshing inventory status: {str(e)}\n{error_details}")
            # Fall back to full reload if update fails
            self.load_inventory_status(current_ideal_quantities)
    
    def _apply_colors_to_row(self, row, percentage, is_group=False):
        """Apply color coding to an entire row based on percentage."""
        # Get base color based on percentage
        base_color = self._get_status_color(percentage)
        
        # Apply color to all cells in the row
        for col in range(7):
            table_item = self.status_table.item(row, col)
            if table_item:  # Make sure item exists before applying color
                table_item.setBackground(base_color)
                
    def _get_status_color(self, percentage):
        """Get the appropriate color for a given percentage."""
        if percentage is None:
            return QColor(240, 240, 240)  # Light Gray for "No Target Set"
        elif percentage == 0:
            return QColor(255, 200, 200)  # Very Light Red for "Out of Stock"
        elif percentage < 20:
            return QColor(255, 200, 200)  # Very Light Red for "Critical - Order Now"
        elif percentage < 50:
            return QColor(255, 220, 180)  # Very Light Orange for "Low - Order Soon"
        elif percentage < 95:
            return QColor(255, 250, 200)  # Very Light Yellow for "Adequate"
        elif percentage < 120:
            return QColor(200, 255, 200)  # Very Light Green for "Optimal"
        else:
            return QColor(230, 210, 255)  # Very Light Purple for "Overstocked"
    
    def manage_filament_links(self):
        """Open a menu to manage filament link groups."""
        # Create a popup menu
        menu = QMenu(self)
        
        # Add actions
        create_action = QAction("Create New Link Group", self)
        create_action.triggered.connect(self.create_link_group)
        menu.addAction(create_action)
        
        # Add a separator
        menu.addSeparator()
        
        # Get existing link groups and add them to the menu
        link_groups = self.db_handler.get_filament_link_groups()
        if link_groups:
            for group in link_groups:
                # Edit group action
                group_action = QAction(f"Edit: {group.name}", self)
                # Store the group ID in the action
                group_action.setData(group.id)
                group_action.triggered.connect(self.edit_link_group)
                menu.addAction(group_action)
                
                # Delete group action
                delete_action = QAction(f"Delete: {group.name}", self)
                delete_action.setData(group.id)
                delete_action.triggered.connect(self.delete_link_group)
                menu.addAction(delete_action)
                
                # Add a separator between groups
                menu.addSeparator()
        else:
            # If no groups exist, add a disabled action
            no_groups_action = QAction("No existing link groups", self)
            no_groups_action.setEnabled(False)
            menu.addAction(no_groups_action)
        
        # Show the menu at the button's position
        menu.exec_(QCursor.pos())
    
    def create_link_group(self):
        """Create a new filament link group."""
        # Get current selection and visible state
        current_row = self.status_table.currentRow()
        scroll_position = self.status_table.verticalScrollBar().value()
        
        # Capture current ideal quantities for ALL filaments BEFORE creating group
        print("--- Starting Create Link Group operation ---")
        current_ideal_quantities = self.capture_current_ideal_quantities()
        
        dialog = FilamentLinkGroupDialog(self, self.db_handler)
        if dialog.exec_():
            print("Link group created, applying preserved quantities")
            
            # Get preserved ideal quantities from the dialog
            preserved_ideal_quantities = current_ideal_quantities.copy()
            
            # Update with any additional quantities from the dialog
            if hasattr(dialog, 'result_data') and 'preserved_ideal_quantities' in dialog.result_data:
                preserved_ideal_quantities.update(dialog.result_data['preserved_ideal_quantities'])
            
            # Use the smart refresh to maintain all ideal quantities
            self.refresh_inventory_status(preserved_ideal_quantities)
            
            # Fix any zero ideal quantities
            self.fix_zero_ideal_quantities(preserved_ideal_quantities)
            
            # Restore selection if possible
            if current_row >= 0 and current_row < self.status_table.rowCount():
                self.status_table.selectRow(current_row)
                
            # Restore scroll position
            self.status_table.verticalScrollBar().setValue(scroll_position)
            print("--- Completed Create Link Group operation ---")
    
    def edit_link_group(self):
        """Edit a filament link group."""
        # Get current selection and visible state
        current_row = self.status_table.currentRow()
        scroll_position = self.status_table.verticalScrollBar().value()
        
        # Capture current ideal quantities for ALL filaments
        current_ideal_quantities = self.capture_current_ideal_quantities()
        
        # Get the group ID from the sender action
        action = self.sender()
        group_id = action.data()
        
        # Open the edit dialog
        dialog = FilamentLinkGroupDialog(self, self.db_handler, group_id)
        if dialog.exec_():
            # Get preserved ideal quantities from the dialog
            preserved_ideal_quantities = current_ideal_quantities.copy()
            if hasattr(dialog, 'result_data') and 'preserved_ideal_quantities' in dialog.result_data:
                preserved_ideal_quantities.update(dialog.result_data['preserved_ideal_quantities'])
            
            # Use the smart refresh to maintain colors
            self.refresh_inventory_status(preserved_ideal_quantities)
            
            # Restore selection if possible
            if current_row >= 0 and current_row < self.status_table.rowCount():
                self.status_table.selectRow(current_row)
                
            # Restore scroll position
            self.status_table.verticalScrollBar().setValue(scroll_position)
    
    def delete_link_group(self):
        """Delete a filament link group."""
        # Get current selection and visible state
        current_row = self.status_table.currentRow()
        scroll_position = self.status_table.verticalScrollBar().value()
        
        # Get the group ID from the sender action
        action = self.sender()
        group_id = action.data()
        
        # Get group info for confirmation message
        group = self.db_handler.get_filament_link_group(group_id)
        if not group:
            QMessageBox.warning(self, "Error", "Group not found")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the group '{group.name}'? "
            f"This will remove the group but not delete any filaments.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                print("--- Starting Delete Link Group operation ---")
                
                # Capture current ideal quantities for ALL filaments before deletion
                current_ideal_quantities = self.capture_current_ideal_quantities()
                
                # Delete the group
                self.db_handler.delete_filament_link_group(group_id)
                print(f"Group '{group.name}' deleted")
                
                # Refresh with preserved ideal quantities
                self.refresh_inventory_status(current_ideal_quantities)
                
                # Fix any zero ideal quantities
                self.fix_zero_ideal_quantities(current_ideal_quantities)
                
                # Restore selection if possible
                if current_row >= 0 and current_row < self.status_table.rowCount():
                    self.status_table.selectRow(current_row)
                    
                # Restore scroll position
                self.status_table.verticalScrollBar().setValue(scroll_position)
                
                QMessageBox.information(self, "Success", f"Group '{group.name}' deleted successfully.")
                print("--- Completed Delete Link Group operation ---")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete group: {str(e)}")
                
    def fix_zero_ideal_quantities(self, preserved_quantities):
        """Check and fix any zero ideal quantities using preserved values."""
        fixed_count = 0
        
        # Scan the entire table for zero ideal quantities
        for row in range(self.status_table.rowCount()):
            # Skip if any items are missing
            if any(self.status_table.item(row, col) is None for col in [0, 1, 2, 4]):
                continue
                
            # Skip group entries
            type_item = self.status_table.item(row, 0)
            if type_item.font().bold():
                continue
                
            # Get filament details
            type_val = type_item.text().strip()
            color_val = self.status_table.item(row, 1).text().strip()
            brand_val = self.status_table.item(row, 2).text().strip()
            
            # Get current ideal qty
            ideal_item = self.status_table.item(row, 4)
            try:
                ideal_qty = float(ideal_item.text() if ideal_item.text() else "0")
                
                # If the ideal quantity is zero but we have a non-zero preserved value
                key = (type_val, color_val, brand_val)
                if ideal_qty == 0 and key in preserved_quantities and preserved_quantities[key] > 0:
                    preserved_value = preserved_quantities[key]
                    print(f"Fixing zero ideal quantity for {type_val} {color_val} {brand_val} to {preserved_value}g")
                    
                    # Update the database
                    self.db_handler.set_ideal_filament_quantity(
                        type_val, color_val, brand_val, preserved_value
                    )
                    
                    # Update the table
                    ideal_item.setText(f"{preserved_value:.1f}")
                    ideal_item.setData(Qt.DisplayRole, preserved_value)
                    
                    # Recalculate difference
                    current_qty = float(self.status_table.item(row, 3).text())
                    diff = current_qty - preserved_value
                    diff_item = self.status_table.item(row, 5)
                    diff_item.setText(f"{diff:.1f}")
                    diff_item.setData(Qt.DisplayRole, diff)
                    
                    # Recalculate percentage
                    percentage = (current_qty / preserved_value * 100) if preserved_value > 0 else None
                    
                    # Update status
                    status_text = self.get_status_text(percentage)
                    status_item = self.status_table.item(row, 6)
                    status_item.setText(status_text)
                    
                    # Update colors
                    self._apply_colors_to_row(row, percentage, False)
                    
                    fixed_count += 1
            except (ValueError, TypeError) as e:
                print(f"Error processing row {row}: {e}")
        
        if fixed_count > 0:
            print(f"Fixed {fixed_count} filaments with zero ideal quantities")
            # Force table update
            self.status_table.viewport().update()
    
    def capture_current_ideal_quantities(self):
        """Capture current ideal quantities for all filaments - with enhanced reliability."""
        # Dictionary to store ideal quantities
        ideal_quantities = {}
        
        print("Capturing current ideal quantities...")
        
        # First, get all ideal quantities from the table
        table_captured = 0
        for row in range(self.status_table.rowCount()):
            # Skip if any items are missing
            if any(self.status_table.item(row, col) is None for col in [0, 1, 2, 4]):
                continue
            
            # Get filament details
            type_item = self.status_table.item(row, 0)
            if type_item is None:
                continue
                
            is_group = type_item.font().bold() if type_item else False
            if is_group:  # Skip group entries
                continue
                
            type_val = type_item.text().strip()
            color_val = self.status_table.item(row, 1).text().strip()
            brand_val = self.status_table.item(row, 2).text().strip()
            
            # Get ideal quantity
            ideal_qty_item = self.status_table.item(row, 4)
            if ideal_qty_item and ideal_qty_item.text():
                try:
                    ideal_qty = float(ideal_qty_item.text())
                    # Always preserve values, even zero, to ensure proper handling
                    ideal_quantities[(type_val, color_val, brand_val)] = ideal_qty
                    table_captured += 1
                except (ValueError, TypeError):
                    pass
        
        print(f"Captured {table_captured} ideal quantities from table")
        
        # Then, add ALL from the database to ensure no values are missed
        db_captured = 0
        try:
            ideal_records = self.db_handler.get_ideal_filament_quantities()
            for record in ideal_records:
                key = (record.type, record.color, record.brand)
                # Only override table values with database values if the database has a higher value
                # This ensures we don't overwrite newly set values with old database values
                if key not in ideal_quantities or (ideal_quantities[key] == 0 and record.ideal_quantity > 0):
                    ideal_quantities[key] = record.ideal_quantity
                    db_captured += 1
        except Exception as e:
            print(f"Error getting ideal quantities from database: {str(e)}")
        
        print(f"Added {db_captured} ideal quantities from database")
        
        return ideal_quantities
    
    def load_inventory_status(self, preserved_ideal_quantities=None):
        """Load inventory status comparing current vs. ideal quantities."""
        try:
            # Get inventory status from database
            inventory_status = self.db_handler.get_inventory_status()
            
            # If we don't have preserved quantities, try to get them from the database
            if not preserved_ideal_quantities:
                print("No preserved quantities provided, capturing from current state")
                preserved_ideal_quantities = self.capture_current_ideal_quantities()
            else:
                print(f"Using provided preserved quantities ({len(preserved_ideal_quantities)} items)")
            
            # Apply preserved quantities to inventory status items
            for item in inventory_status:
                if not item.get('is_group', False):
                    key = (item['type'], item['color'], item['brand'])
                    
                    # First check if we have a preserved quantity for this exact filament
                    if key in preserved_ideal_quantities:
                        # If database has zero but preserved is non-zero, update the database
                        if item['ideal_quantity'] == 0 and preserved_ideal_quantities[key] > 0:
                            print(f"Fixing ideal quantity for {key[0]} {key[1]} {key[2]} from 0g to {preserved_ideal_quantities[key]}g")
                            # Update database
                            self.db_handler.set_ideal_filament_quantity(
                                key[0], key[1], key[2], preserved_ideal_quantities[key]
                            )
                        
                        # Update the item with preserved quantity
                        item['ideal_quantity'] = preserved_ideal_quantities[key]
                        
                    # Case-insensitive matching if needed
                    elif item['ideal_quantity'] == 0:
                        # Try to find a case-insensitive match
                        for p_key, p_value in preserved_ideal_quantities.items():
                            if (p_key[0].upper() == item['type'].upper() and 
                                p_key[1].upper() == item['color'].upper() and
                                p_key[2].upper() == item['brand'].upper() and
                                p_value > 0):
                                print(f"Case-insensitive match found for {item['type']} {item['color']} {item['brand']}")
                                item['ideal_quantity'] = p_value
                                
                                # Update database
                                self.db_handler.set_ideal_filament_quantity(
                                    item['type'], item['color'], item['brand'], p_value
                                )
                                break
                    
                    # Recalculate difference and percentage
                    item['difference'] = item['current_quantity'] - item['ideal_quantity']
                    if item['ideal_quantity'] > 0:
                        item['percentage'] = (item['current_quantity'] / item['ideal_quantity'] * 100)
                    else:
                        item['percentage'] = None
            
            # Set table rows
            self.status_table.setRowCount(len(inventory_status))
            
            for row, item in enumerate(inventory_status):
                # Set filament details
                is_group = item.get('is_group', False)
                
                # Create items
                type_item = QTableWidgetItem(item['type'])
                color_item = QTableWidgetItem(item['color'])
                brand_item = QTableWidgetItem(item['brand'])
                
                # Set bold font for group items
                if is_group:
                    font = type_item.font()
                    font.setBold(True)
                    type_item.setFont(font)
                    color_item.setFont(font)
                    brand_item.setFont(font)
                    
                    # Store group ID
                    type_item.setData(Qt.UserRole, item['group_id'])
                    
                    # Add tooltip with group name and description
                    tooltip = f"Group: {item['group_name']}"
                    type_item.setToolTip(tooltip)
                    color_item.setToolTip(tooltip)
                    brand_item.setToolTip(tooltip)
                
                # Add items to table
                self.status_table.setItem(row, 0, type_item)
                self.status_table.setItem(row, 1, color_item)
                self.status_table.setItem(row, 2, brand_item)
                
                # Current quantity
                current_qty_item = QTableWidgetItem()
                current_qty_item.setData(Qt.DisplayRole, item['current_quantity'])
                current_qty_item.setText(f"{item['current_quantity']:.1f}")
                if is_group:
                    current_qty_item.setFont(font)
                self.status_table.setItem(row, 3, current_qty_item)
                
                # Ideal quantity
                ideal_qty_item = QTableWidgetItem()
                ideal_qty_item.setData(Qt.DisplayRole, item['ideal_quantity'])
                ideal_qty_item.setText(f"{item['ideal_quantity']:.1f}")
                if is_group:
                    ideal_qty_item.setFont(font)
                self.status_table.setItem(row, 4, ideal_qty_item)
                
                # Difference
                diff_qty_item = QTableWidgetItem()
                diff_qty_item.setData(Qt.DisplayRole, item['difference'])
                diff_qty_item.setText(f"{item['difference']:.1f}")
                if is_group:
                    diff_qty_item.setFont(font)
                self.status_table.setItem(row, 5, diff_qty_item)
                
                # Get percentage and ensure it's properly calculated
                percentage = item['percentage']
                
                # Status text
                status_text = self.get_status_text(percentage)
                status_item = QTableWidgetItem(status_text)
                if is_group:
                    status_item.setFont(font)
                self.status_table.setItem(row, 6, status_item)
                
                # Apply color coding based on inventory status - do this after all items are set
                # Use the new _apply_colors_to_row method to ensure consistent coloring
                self._apply_colors_to_row(row, percentage, is_group)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "Error", f"Failed to load inventory status: {str(e)}\n\nDetails:\n{error_details}")
            
    def get_status_text(self, percentage):
        """Get status text based on percentage of ideal quantity."""
        if percentage is None:
            return "No Target Set"
        elif percentage == 0:
            return "Out of Stock"
        elif percentage < 20:
            return "Critical - Order Now"
        elif percentage < 50:
            return "Low - Order Soon"
        elif percentage < 95:
            return "Adequate"
        elif percentage < 120:
            return "Optimal"
        else:
            return "Overstocked"

    def color_code_status_item(self, item, percentage):
        """Apply color coding to inventory status table item."""
        if item is None:
            return  # Skip if item is None
            
        color = None
        if percentage is None:
            color = QColor(240, 240, 240)  # Light Gray for "No Target Set"
        elif percentage == 0:
            color = QColor(255, 200, 200)  # Very Light Red for "Out of Stock"
        elif percentage < 20:
            color = QColor(255, 200, 200)  # Very Light Red for "Critical - Order Now"
        elif percentage < 50:
            color = QColor(255, 220, 180)  # Very Light Orange for "Low - Order Soon"
        elif percentage < 95:
            color = QColor(255, 250, 200)  # Very Light Yellow for "Adequate"
        elif percentage < 120:
            color = QColor(200, 255, 200)  # Very Light Green for "Optimal"
        else:
            color = QColor(230, 210, 255)  # Very Light Purple for "Overstocked"
            
        # Apply the color to the item
        item.setBackground(color)
        return color