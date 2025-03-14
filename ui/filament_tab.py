"""
Filament inventory management tab.
"""
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel, 
                             QLineEdit, QDoubleSpinBox, QComboBox, QMessageBox,
                             QHeaderView, QFormLayout, QDateEdit, QTabWidget,
                             QSplitter, QDialog, QDialogButtonBox, QInputDialog,
                             QListWidget, QListWidgetItem, QPlainTextEdit, QCheckBox,
                             QMenu, QAction, QScrollArea, QSpinBox)
from PyQt5.QtCore import Qt, QDate, QSortFilterProxyModel, QTimer, pyqtSignal
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
        price_layout = QVBoxLayout()
        price_input_layout = QHBoxLayout()
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000)
        self.price_input.setValue(25)  # Default price
        self.price_input.setPrefix("$ ")
        price_input_layout.addWidget(self.price_input)
        price_layout.addLayout(price_input_layout)
        
        # Quick price buttons
        quick_price_layout = QHBoxLayout()
        quick_price_values = [13, 14, 15, 25, 30]
        
        for price in quick_price_values:
            btn = QPushButton(f"${price}")
            btn.setMaximumWidth(40)  # Make buttons compact
            btn.clicked.connect(lambda checked, p=price: self.price_input.setValue(p))
            quick_price_layout.addWidget(btn)
        
        quick_price_layout.addStretch()
        price_layout.addLayout(quick_price_layout)
        
        form_layout.addRow("Price:", price_layout)
        
        # Purchase date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if self.filament_data and 'purchase_date' in self.filament_data:
            self.date_input.setDate(self.filament_data.get('purchase_date', QDate.currentDate()))
        else:
            self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Purchase Date:", self.date_input)
        
        # Number of spools to add
        self.spool_count_input = QSpinBox()
        self.spool_count_input.setRange(1, 100)
        self.spool_count_input.setValue(1)
        if self.filament_data:  # In edit mode, we don't need the spool count
            self.spool_count_input.hide()
        else:
            form_layout.addRow("Number of Spools:", self.spool_count_input)
        
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
            'purchase_date': self.date_input.date(),
            'spool_count': self.spool_count_input.value() if hasattr(self, 'spool_count_input') else 1
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
    
    filament_updated = pyqtSignal()
    
    def __init__(self, db_handler):
        """Initialize filament tab."""
        super().__init__()
        
        self.db_handler = db_handler
        self.modified_filaments = set()
        self.modified_brands = set()
        self.modified_types = set()
        self.modified_colors = set()
        self.populate_type_signal = None
        
        # Track orientation state
        self.is_portrait = False
        
        self.setup_ui()
        self.connect_signals()
        self.load_data()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create tab widget for sub-tabs
        self.sub_tabs = QTabWidget()
        
        # Create inventory tab
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(inventory_tab)
        
        # Create a splitter for inventory
        self.inventory_splitter = QSplitter(Qt.Vertical)
        
        # Create filament control panel at top
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create add/edit buttons section
        button_layout = QHBoxLayout()
        
        # Add filament button
        add_button = QPushButton("Add Filament")
        add_button.clicked.connect(self.add_filament)
        button_layout.addWidget(add_button)
        
        # Edit filament button
        edit_button = QPushButton("Edit Filament")
        edit_button.clicked.connect(self.edit_filament)
        button_layout.addWidget(edit_button)
        
        # Delete filament button
        delete_button = QPushButton("Delete Filament")
        delete_button.clicked.connect(self.delete_filament)
        button_layout.addWidget(delete_button)
        
        control_layout.addLayout(button_layout)
        
        # Create filters for inventory
        filter_layout = QHBoxLayout()
        
        # Filament type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.setMinimumWidth(100)
        self.type_filter.currentTextChanged.connect(self.filter_filament_table)
        type_layout.addWidget(self.type_filter)
        filter_layout.addLayout(type_layout)
        
        # Search filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search by color, brand or type...")
        self.search_filter.textChanged.connect(self.filter_filament_table)
        search_layout.addWidget(self.search_filter)
        filter_layout.addLayout(search_layout)
        
        control_layout.addLayout(filter_layout)
        
        # Create filament table
        self.filament_table = QTableWidget()
        self.filament_table.setColumnCount(8)
        self.filament_table.setHorizontalHeaderLabels([
            "ID", "Type", "Color", "Brand", "Remaining (g)", 
            "Spool Weight (g)", "% Remaining", "Price"
        ])
        
        # Enable sorting
        self.filament_table.setSortingEnabled(True)
        self.filament_table.horizontalHeader().setSectionsClickable(True)
        self.filament_table.horizontalHeader().sectionClicked.connect(self.sort_filament_table)
        
        # Make all columns stretch to fill available space
        self.filament_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.filament_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Add to control panel
        control_layout.addWidget(self.filament_table)
        self.inventory_splitter.addWidget(control_panel)
        
        # Create aggregated view widget
        agg_widget = QWidget()
        agg_layout = QVBoxLayout(agg_widget)
        agg_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add label
        agg_layout.addWidget(QLabel("<h3>Aggregated Inventory</h3>"))
        agg_layout.addWidget(QLabel("Shows total weight of each filament type/color/brand combination"))
        
        # Search for aggregated table
        agg_search_layout = QHBoxLayout()
        agg_search_layout.addWidget(QLabel("Search:"))
        self.agg_search_filter = QLineEdit()
        self.agg_search_filter.setPlaceholderText("Search aggregated inventory...")
        self.agg_search_filter.textChanged.connect(self.filter_aggregated_table)
        agg_search_layout.addWidget(self.agg_search_filter)
        agg_layout.addLayout(agg_search_layout)
        
        # Create aggregated table
        self.aggregated_table = QTableWidget()
        self.aggregated_table.setColumnCount(7)
        self.aggregated_table.setHorizontalHeaderLabels([
            "Type", "Color", "Brand", "Total Weight (g)", 
            "Remaining (g)", "% Remaining", "Spools"
        ])
        
        # Enable sorting
        self.aggregated_table.setSortingEnabled(True)
        self.aggregated_table.horizontalHeader().setSectionsClickable(True)
        self.aggregated_table.horizontalHeader().sectionClicked.connect(self.sort_aggregated_table)
        
        # Configure column stretching
        self.aggregated_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.aggregated_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        agg_layout.addWidget(self.aggregated_table)
        self.inventory_splitter.addWidget(agg_widget)
        
        # Add widgets to inventory tab layout
        inventory_layout.addWidget(self.inventory_splitter)
        
        inventory_tab.setLayout(inventory_layout)
        
        # Add tab to sub-tabs
        self.sub_tabs.addTab(inventory_tab, "Inventory")
        
        # Add status tab
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
        
        # Add tab to sub-tabs
        self.sub_tabs.addTab(status_tab, "Status")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.sub_tabs)
        
        self.setLayout(main_layout)
        
    def adjust_for_portrait(self, is_portrait):
        """Adjust the layout based on screen orientation."""
        self.is_portrait = is_portrait
        
        if is_portrait:
            # Vertical monitor adjustments
            
            # Set tab orientation
            if hasattr(self, 'sub_tabs'):
                self.sub_tabs.setTabPosition(QTabWidget.West)  # Tabs on the left in portrait
            
            # Optimize table column widths for narrower display
            if hasattr(self, 'filament_table'):
                header = self.filament_table.horizontalHeader()
                header.resizeSections(QHeaderView.ResizeToContents)
                
                # Make some columns fixed width and narrower
                for col_idx, col_width in [
                    (0, 40),    # ID column
                    (1, 100),   # Type column
                    (2, 80),    # Color column
                    (3, 90),    # Brand column
                    (4, 80),    # Remaining column
                    (5, 80),    # Spool Weight column
                    (6, 60)     # Price column
                ]:
                    if col_idx < self.filament_table.columnCount():
                        header.setSectionResizeMode(col_idx, QHeaderView.Fixed)
                        header.resizeSection(col_idx, col_width)
            
            # Also adjust aggregated table
            if hasattr(self, 'aggregated_table'):
                header = self.aggregated_table.horizontalHeader()
                header.resizeSections(QHeaderView.ResizeToContents)
                
                # Make certain columns fixed width
                for col_idx, col_width in [
                    (0, 100),    # Type column
                    (1, 80),     # Color column
                    (2, 90),     # Brand column
                    (3, 80),     # Total Quantity column
                    (4, 80),     # Remaining column
                    (5, 60),     # % Remaining column
                    (6, 50)      # Spools column
                ]:
                    if col_idx < self.aggregated_table.columnCount():
                        header.setSectionResizeMode(col_idx, QHeaderView.Fixed)
                        header.resizeSection(col_idx, col_width)
            
            # Adjust status table
            if hasattr(self, 'status_table'):
                header = self.status_table.horizontalHeader()
                header.resizeSections(QHeaderView.ResizeToContents)
                
                # Fixed width columns
                for col_idx, col_width in [
                    (0, 100),    # Type column
                    (1, 80),     # Color column
                    (2, 90),     # Brand column
                    (3, 70),     # Current column
                    (4, 70),     # Ideal column
                    (5, 70),     # Difference column
                    (6, 60)      # Status column
                ]:
                    if col_idx < self.status_table.columnCount():
                        header.setSectionResizeMode(col_idx, QHeaderView.Fixed)
                        header.resizeSection(col_idx, col_width)
                
        else:
            # Reset to landscape mode (horizontal monitor)
            
            # Reset tab orientation
            if hasattr(self, 'sub_tabs'):
                self.sub_tabs.setTabPosition(QTabWidget.North)  # Tabs on top in landscape
            
            # Reset table columns to default interactive mode
            for table_attr in ['filament_table', 'aggregated_table', 'status_table']:
                if hasattr(self, table_attr):
                    table = getattr(self, table_attr)
                    header = table.horizontalHeader()
                    for i in range(table.columnCount()):
                        header.setSectionResizeMode(i, QHeaderView.Interactive)
                    header.resizeSections(QHeaderView.ResizeToContents)
        
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
        """Filter filament table based on search input and filter criteria."""
        try:
            search_text = self.search_filter.text().lower()
            type_filter = self.type_filter.currentText()
            
            for row in range(self.filament_table.rowCount()):
                match = False
                
                # Check if row matches the type filter
                if type_filter and type_filter != "All":
                    type_cell = self.filament_table.item(row, 1)
                    if type_cell and type_filter == type_cell.text():
                        match = True
                else:
                    match = True
                
                # Apply search filter if there's search text
                if search_text and match:
                    match = False
                    for col in range(1, 4):  # Check type, color, brand columns
                        cell = self.filament_table.item(row, col)
                        if cell and search_text in cell.text().lower():
                            match = True
                            break
                
                self.filament_table.setRowHidden(row, not match)
        except Exception as e:
            print(f"Error filtering filament table: {str(e)}")
            # Don't hide any rows if there's an error
            for row in range(self.filament_table.rowCount()):
                self.filament_table.setRowHidden(row, False)
    
    def filter_aggregated_table(self):
        """Filter the aggregated table based on search input and criteria."""
        try:
            search_text = self.agg_search_filter.text().lower()
            
            for row in range(self.aggregated_table.rowCount()):
                match = False
                
                # Apply search filter if there's search text
                if search_text:
                    match = False
                    for col in range(3):  # Check type, color, brand columns
                        cell = self.aggregated_table.item(row, col)
                        if cell and search_text in cell.text().lower():
                            match = True
                            break
                else:
                    match = True
                
                self.aggregated_table.setRowHidden(row, not match)
        except Exception as e:
            print(f"Error filtering aggregated table: {str(e)}")
            # Don't hide any rows if there's an error
            for row in range(self.aggregated_table.rowCount()):
                self.aggregated_table.setRowHidden(row, False)

    def on_filament_cell_changed(self, row, column):
        """Handle filament table cell changes."""
        if column > 0:  # Ignore ID column
            filament_id = self.filament_table.item(row, 0).data(Qt.UserRole)
            if filament_id:
                self.modified_filaments.add(filament_id)
                # Set filament name in bold to indicate unsaved changes
                item = self.filament_table.item(row, 1)
                if item:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
    
    def on_brand_cell_changed(self, row, column):
        """Handle brand table cell changes."""
        if column > 0:  # Ignore ID column
            brand_id = self.brand_table.item(row, 0).data(Qt.UserRole)
            if brand_id:
                self.modified_brands.add(brand_id)
                # Set brand name in bold to indicate unsaved changes
                item = self.brand_table.item(row, 1)
                font = item.font()
                font.setBold(True)
                item.setFont(font)

    def on_type_cell_changed(self, row, column):
        """Handle filament type table cell changes."""
        if column > 0:  # Ignore ID column
            type_id = self.type_table.item(row, 0).data(Qt.UserRole)
            if type_id:
                self.modified_types.add(type_id)
                # Set type name in bold to indicate unsaved changes
                item = self.type_table.item(row, 1)
                font = item.font()
                font.setBold(True)
                item.setFont(font)

    def on_color_cell_changed(self, row, column):
        """Handle color table cell changes."""
        if column > 0:  # Ignore ID column
            color_id = self.color_table.item(row, 0).data(Qt.UserRole)
            if color_id:
                self.modified_colors.add(color_id)
                # Set color name in bold to indicate unsaved changes
                item = self.color_table.item(row, 1)
                font = item.font()
                font.setBold(True)
                item.setFont(font)

    def connect_signals(self):
        """Connect signals to handle table cell changes."""
        # Connect filament table changes
        self.filament_table.cellChanged.connect(self.on_filament_cell_changed)
        
        # Since we don't have brand_table, type_table, or color_table,
        # we'll only track changes to the filament_table
        
    def load_data(self):
        """Load all required data."""
        self.load_filaments()
        self.load_aggregated_inventory()
        self.load_inventory_status()  # Load inventory status comparison
        self.populate_dynamic_dropdowns()
        
        # Add a timer to refresh the inventory status once on startup
        # This ensures all colors are properly loaded after initialization
        QTimer.singleShot(100, self.refresh_inventory_status)

    def save_filament_changes(self, row):
        """Save changes to a filament in the database."""
        try:
            # Get filament data from the table
            filament_id = self.filament_table.item(row, 0).data(Qt.UserRole)
            
            # Get values from the table cells
            filament_type = self.filament_table.item(row, 1).text()
            color = self.filament_table.item(row, 2).text()
            brand = self.filament_table.item(row, 3).text()
            
            # Get quantity remaining (column 4)
            quantity_remaining = 0.0  # Default
            if self.filament_table.item(row, 4):
                try:
                    quantity_remaining = float(self.filament_table.item(row, 4).text())
                except (ValueError, TypeError):
                    pass
            
            # Get spool weight (column 5)
            spool_weight = 1000.0  # Default
            if self.filament_table.item(row, 5):
                try:
                    spool_weight = float(self.filament_table.item(row, 5).text())
                except (ValueError, TypeError):
                    pass
            
            # Get price (column 7)
            price = 0.0  # Default
            if self.filament_table.item(row, 7):
                try:
                    price_text = self.filament_table.item(row, 7).text()
                    if price_text != "N/A":
                        price = float(price_text)
                except (ValueError, TypeError):
                    pass
            
            # Default purchase date is today
            purchase_date = datetime.date.today().isoformat()
            
            # Update filament in database
            self.db_handler.update_filament(
                filament_id=filament_id,
                filament_type=filament_type,
                color=color,
                brand=brand,
                spool_weight=spool_weight,
                quantity_remaining=quantity_remaining,
                price=price,
                purchase_date=purchase_date
            )
            
            # Reset the font weight to normal
            for col in range(1, self.filament_table.columnCount()):
                item = self.filament_table.item(row, col)
                if item:
                    font = item.font()
                    font.setBold(False)
                    item.setFont(font)
            
            # Update other views that depend on filament data
            self.load_aggregated_inventory()
            self.load_inventory_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save filament changes: {str(e)}")

    def add_filament(self):
        """Add a new filament to the database."""
        dialog = FilamentDialog(self)
        if dialog.exec_():
            filament_data = dialog.get_data()
            try:
                self.db_handler.add_filament(
                    filament_type=filament_data.get('type', ''),
                    color=filament_data.get('color', ''),
                    brand=filament_data.get('brand', ''),
                    spool_weight=filament_data.get('spool_weight', 0),
                    quantity_remaining=filament_data.get('remaining_weight', 0),
                    price=filament_data.get('price', 0),
                    purchase_date=filament_data.get('purchase_date', None)
                )
                self.load_filaments()
                self.load_aggregated_inventory()
                self.load_inventory_status()
                
                # Emit signal to notify that filament data has been updated
                self.filament_updated.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add filament: {str(e)}")
    
    def edit_filament(self):
        """Edit the selected filament."""
        selected_rows = self.filament_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a filament to edit.")
            return
            
        # Get the filament ID from the first column of the selected row
        row = selected_rows[0].row()
        filament_id = int(self.filament_table.item(row, 0).text())
        
        # Get current filament data
        filament = self.db_handler.get_filament_by_id(filament_id)
        if not filament:
            QMessageBox.warning(self, "Not Found", "Selected filament not found in database.")
            return
            
        # Create filament data dictionary with correct attribute names
        filament_data = {
            'type': filament.type,
            'color': filament.color,
            'brand': filament.brand,
            'spool_weight': filament.spool_weight,
            'remaining_weight': filament.quantity_remaining,  # Use quantity_remaining instead of remaining_weight
            'price': filament.price,
            'purchase_date': filament.purchase_date
        }
        
        # Create and show the dialog
        dialog = FilamentDialog(self, filament_data)
        if dialog.exec_():
            updated_data = dialog.get_data()
            
            try:
                self.db_handler.update_filament(
                    filament_id=filament_id,
                    filament_type=updated_data.get('type', ''),
                    color=updated_data.get('color', ''),
                    brand=updated_data.get('brand', ''),
                    spool_weight=updated_data.get('spool_weight', 0),
                    quantity_remaining=updated_data.get('remaining_weight', 0),  # Map remaining_weight to quantity_remaining
                    price=updated_data.get('price', 0),
                    purchase_date=updated_data.get('purchase_date', None)
                )
                self.load_filaments()
                self.load_aggregated_inventory()
                self.load_inventory_status()
                
                # Emit signal to notify that filament data has been updated
                self.filament_updated.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update filament: {str(e)}")
    
    def delete_filament(self):
        """Delete the selected filament."""
        selected_rows = self.filament_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a filament to delete.")
            return
            
        # Get the filament ID from the first column of the selected row
        row = selected_rows[0].row()
        filament_id = int(self.filament_table.item(row, 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            "Are you sure you want to delete this filament?\n\n"
            "Note: If this filament is used in any print jobs, it cannot be deleted.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_handler.delete_filament(filament_id)
                self.load_filaments()
                self.load_aggregated_inventory()
                self.load_inventory_status()
                
                # Emit signal to notify that filament data has been updated
                self.filament_updated.emit()
                
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete filament: {str(e)}")
    
    def set_ideal_quantity(self):
        """Set the ideal quantity for a filament type/color combination."""
        # Get selected row from status table
        selected_rows = self.status_table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a filament type/color to set ideal quantity.")
            return
            
        row = selected_rows[0].row()
        
        # Get type and check if it's a group
        type_text = self.status_table.item(row, 0).text()
        is_group = type_text.startswith("Group: ")
        
        # For groups, we need to handle differently
        if is_group:
            group_name = type_text.replace("Group: ", "", 1)
            
            # Find the group ID
            groups = self.db_handler.get_filament_link_groups()
            group_id = None
            for group in groups:
                if group.name == group_name:
                    group_id = group.id
                    break
                    
            if not group_id:
                QMessageBox.warning(self, "Error", f"Group '{group_name}' not found.")
                return
                
            # Get current ideal value from table
            current_ideal = self.status_table.item(row, 4).text()
            try:
                current_ideal_value = float(current_ideal)
            except (ValueError, TypeError):
                current_ideal_value = 0
                
            # Ask for new ideal quantity
            new_ideal, ok = QInputDialog.getDouble(
                self,
                "Set Ideal Quantity for Group",
                f"Enter ideal quantity for group '{group_name}' (in grams):",
                current_ideal_value,
                0,
                100000,
                2
            )
            
            if ok:
                try:
                    # Update the group's ideal quantity
                    self.db_handler.update_filament_link_group(
                        group_id,
                        ideal_quantity=new_ideal
                    )
                    self.load_inventory_status()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to set ideal quantity: {str(e)}")
        else:
            # Regular filament (not a group)
            filament_color = self.status_table.item(row, 1).text()
            filament_brand = self.status_table.item(row, 2).text()
            current_ideal = self.status_table.item(row, 4).text()
            
            try:
                current_ideal_value = float(current_ideal)
            except (ValueError, TypeError):
                current_ideal_value = 0
                
            # Ask for new ideal quantity
            new_ideal, ok = QInputDialog.getDouble(
                self,
                "Set Ideal Quantity",
                f"Enter ideal quantity for {type_text} {filament_color} (in grams):",
                current_ideal_value,
                0,
                100000,
                2
            )
            
            if ok:
                try:
                    self.db_handler.set_ideal_filament_quantity(type_text, filament_color, filament_brand, new_ideal)
                    self.load_inventory_status()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to set ideal quantity: {str(e)}")
    
    def manage_filament_links(self):
        """Open dialog to manage filament link groups."""
        # Create a dialog to show existing groups
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Filament Link Groups")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add label
        layout.addWidget(QLabel("<h3>Filament Link Groups</h3>"))
        layout.addWidget(QLabel("Link similar filaments together to track inventory as a group"))
        
        # Add list of existing groups
        group_list = QListWidget()
        group_list.setSelectionMode(QListWidget.SingleSelection)
        
        # Populate list with existing groups
        groups = self.db_handler.get_filament_link_groups()
        for group in groups:
            item_text = f"{group.name} ({len(group.filament_links)} filaments)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, group.id)
            group_list.addItem(item)
            
        layout.addWidget(group_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        create_button = QPushButton("Create New Group")
        edit_button = QPushButton("Edit Selected Group")
        delete_button = QPushButton("Delete Selected Group")
        
        # Connect buttons
        create_button.clicked.connect(lambda: self._create_filament_group(dialog))
        edit_button.clicked.connect(lambda: self._edit_filament_group(dialog, group_list))
        delete_button.clicked.connect(lambda: self._delete_filament_group(dialog, group_list))
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
        # Refresh inventory status to reflect any changes to link groups
        self.load_inventory_status()
    
    def _create_filament_group(self, parent_dialog):
        """Create a new filament link group."""
        dialog = FilamentLinkGroupDialog(self, self.db_handler)
        if dialog.exec_():
            # Refresh the parent dialog list
            self._refresh_group_list(parent_dialog)
    
    def _edit_filament_group(self, parent_dialog, group_list):
        """Edit a selected filament link group."""
        selected_items = group_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a group to edit.")
            return
            
        group_id = selected_items[0].data(Qt.UserRole)
        dialog = FilamentLinkGroupDialog(self, self.db_handler, group_id)
        if dialog.exec_():
            # Refresh the parent dialog list
            self._refresh_group_list(parent_dialog)
    
    def _delete_filament_group(self, parent_dialog, group_list):
        """Delete a selected filament link group."""
        selected_items = group_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a group to delete.")
            return
            
        group_id = selected_items[0].data(Qt.UserRole)
        
        # Ask for confirmation
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this group? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            try:
                self.db_handler.delete_filament_link_group(group_id)
                QMessageBox.information(self, "Success", "Group deleted successfully.")
                # Refresh the parent dialog list
                self._refresh_group_list(parent_dialog)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete group: {str(e)}")
    
    def _refresh_group_list(self, dialog):
        """Refresh the group list in the parent dialog."""
        group_list = None
        
        # Find the QListWidget in the dialog
        for child in dialog.findChildren(QListWidget):
            group_list = child
            break
            
        if group_list:
            # Clear the list
            group_list.clear()
            
            # Repopulate with updated data
            groups = self.db_handler.get_filament_link_groups()
            for group in groups:
                item_text = f"{group.name} ({len(group.filament_links)} filaments)"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, group.id)
                group_list.addItem(item)

    def refresh_inventory_status(self):
        """Refresh the inventory status display."""
        self.load_inventory_status()

    def has_unsaved_changes(self):
        """Check if there are any unsaved changes in the filament tab."""
        return (len(self.modified_filaments) > 0 or 
                len(self.modified_brands) > 0 or 
                len(self.modified_types) > 0 or 
                len(self.modified_colors) > 0)
    
    def save_all_changes(self):
        """Save all pending changes in the filament tab."""
        # Save any modified filaments
        for filament_id in self.modified_filaments:
            # Find the row with this filament ID
            for row in range(self.filament_table.rowCount()):
                if self.filament_table.item(row, 0) and self.filament_table.item(row, 0).data(Qt.UserRole) == filament_id:
                    self.save_filament_changes(row)
                    break
        
        # Clear modification tracking
        self.modified_filaments.clear()
        self.modified_brands.clear()
        self.modified_types.clear()
        self.modified_colors.clear()
        
        # Emit signal to notify that filament data has been updated
        self.filament_updated.emit()

    def populate_dynamic_dropdowns(self):
        """Populate dynamic dropdowns with data from the database."""
        # Populate type filter dropdown
        self.type_filter.clear()
        self.type_filter.addItem("All")
        
        types = self.db_handler.get_filament_types()
        for filament_type in types:
            # Check if filament_type is a string or an object with a name attribute
            if isinstance(filament_type, str):
                self.type_filter.addItem(filament_type)
            else:
                self.type_filter.addItem(filament_type.name)

    def load_filaments(self):
        """Load filaments from the database and display in the table."""
        try:
            # Get filaments from database
            filaments = self.db_handler.get_filaments()
            
            # Remember current sort settings
            sort_column = self.filament_table.horizontalHeader().sortIndicatorSection()
            sort_order = self.filament_table.horizontalHeader().sortIndicatorOrder()
            
            # Temporarily disable sorting to improve performance
            self.filament_table.setSortingEnabled(False)
            
            # Clear table and set row count
            self.filament_table.setRowCount(len(filaments))
            
            # Populate table with filament data
            for row, filament in enumerate(filaments):
                # ID column (hidden from view but used for reference)
                id_item = QTableWidgetItem(str(filament.id))
                id_item.setData(Qt.UserRole, filament.id)
                self.filament_table.setItem(row, 0, id_item)
                
                # Type column
                self.filament_table.setItem(row, 1, QTableWidgetItem(filament.type))
                
                # Color column
                self.filament_table.setItem(row, 2, QTableWidgetItem(filament.color))
                
                # Brand column
                self.filament_table.setItem(row, 3, QTableWidgetItem(filament.brand))
                
                # Remaining weight column
                remaining_item = QTableWidgetItem()
                remaining_item.setData(Qt.DisplayRole, float(filament.quantity_remaining))
                remaining_item.setText(f"{filament.quantity_remaining:.1f}")
                self.filament_table.setItem(row, 4, remaining_item)
                
                # Spool weight column
                spool_item = QTableWidgetItem()
                spool_item.setData(Qt.DisplayRole, float(filament.spool_weight))
                spool_item.setText(f"{filament.spool_weight:.1f}")
                self.filament_table.setItem(row, 5, spool_item)
                
                # Percentage remaining column
                if filament.spool_weight > 0:
                    percentage = (filament.quantity_remaining / filament.spool_weight) * 100
                else:
                    percentage = 0
                    
                percentage_item = QTableWidgetItem()
                percentage_item.setData(Qt.DisplayRole, float(percentage))
                percentage_item.setText(f"{percentage:.1f}%")
                self.filament_table.setItem(row, 6, percentage_item)
                
                # Price column
                if filament.price:
                    price_item = QTableWidgetItem()
                    price_item.setData(Qt.DisplayRole, float(filament.price))
                    price_item.setText(f"{filament.price:.2f}")
                    self.filament_table.setItem(row, 7, price_item)
                else:
                    self.filament_table.setItem(row, 7, QTableWidgetItem("N/A"))
                
                # Color code rows based on percentage
                self._apply_colors_to_filament_row(row, percentage)
            
            # Re-enable sorting and restore previous sort
            self.filament_table.setSortingEnabled(True)
            if sort_column >= 0:
                self.filament_table.sortByColumn(sort_column, sort_order)
                
            # Refresh filters after loading
            self.filter_filament_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load filaments: {str(e)}")
            
    def _apply_colors_to_filament_row(self, row, percentage):
        """Apply color coding to a filament table row based on percentage remaining."""
        # Apply color to each cell in the row
        for col in range(self.filament_table.columnCount()):
            cell_item = self.filament_table.item(row, col)
            if cell_item:
                color = self._get_status_color(percentage)
                cell_item.setBackground(color)
    
    def _get_status_color(self, percentage):
        """Get the color for a status based on percentage."""
        if percentage == 0:
            return QColor(240, 240, 240)  # Light gray
        elif percentage < 20:
            return QColor(255, 200, 200)  # Light red
        elif percentage < 40:
            return QColor(255, 235, 156)  # Light orange
        elif percentage < 60:
            return QColor(255, 255, 200)  # Light yellow
        elif percentage < 80:
            return QColor(200, 235, 255)  # Light blue
        else:
            return QColor(200, 255, 200)  # Light green
    
    def load_aggregated_inventory(self):
        """Load aggregated filament inventory from database."""
        try:
            # Get aggregated inventory data
            inventory = self.db_handler.get_aggregated_filament_inventory()
            
            if not inventory:
                # Clear the table if no inventory data
                self.aggregated_table.setRowCount(0)
                return
                
            # Remember current sort settings
            sort_column = self.aggregated_table.horizontalHeader().sortIndicatorSection()
            sort_order = self.aggregated_table.horizontalHeader().sortIndicatorOrder()
            
            # Temporarily disable sorting to improve performance
            self.aggregated_table.setSortingEnabled(False)
            
            # Clear table and set row count
            self.aggregated_table.setRowCount(len(inventory))
            
            # Populate table with aggregated inventory data
            for row, item in enumerate(inventory):
                # Type column
                self.aggregated_table.setItem(row, 0, QTableWidgetItem(item['type']))
                
                # Color column
                self.aggregated_table.setItem(row, 1, QTableWidgetItem(item['color']))
                
                # Brand column
                self.aggregated_table.setItem(row, 2, QTableWidgetItem(item['brand']))
                
                # Total weight column
                total_weight_item = QTableWidgetItem()
                total_weight_item.setData(Qt.DisplayRole, float(item['total_quantity']))
                total_weight_item.setText(f"{item['total_quantity']:.1f}")
                self.aggregated_table.setItem(row, 3, total_weight_item)
                
                # Remaining weight column
                remaining_weight_item = QTableWidgetItem()
                remaining_weight_item.setData(Qt.DisplayRole, float(item['quantity_remaining']))
                remaining_weight_item.setText(f"{item['quantity_remaining']:.1f}")
                self.aggregated_table.setItem(row, 4, remaining_weight_item)
                
                # Percentage remaining column
                if item['total_quantity'] > 0:
                    percentage = (item['quantity_remaining'] / item['total_quantity']) * 100
                else:
                    percentage = 0
                    
                percentage_item = QTableWidgetItem()
                percentage_item.setData(Qt.DisplayRole, float(percentage))
                percentage_item.setText(f"{percentage:.1f}%")
                self.aggregated_table.setItem(row, 5, percentage_item)
                
                # Spools column
                spools_item = QTableWidgetItem()
                spools_item.setData(Qt.DisplayRole, int(item['spool_count']))
                spools_item.setText(str(item['spool_count']))
                self.aggregated_table.setItem(row, 6, spools_item)
                
                # Color code rows based on percentage
                self._apply_colors_to_aggregated_row(row, percentage)
            
            # Re-enable sorting and restore previous sort
            self.aggregated_table.setSortingEnabled(True)
            if sort_column >= 0:
                self.aggregated_table.sortByColumn(sort_column, sort_order)
                
            # Refresh filters after loading
            self.filter_aggregated_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load aggregated inventory: {str(e)}")
    
    def _apply_colors_to_aggregated_row(self, row, percentage):
        """Apply color coding to an aggregated table row based on percentage remaining."""
        # Apply color to each cell in the row
        for col in range(self.aggregated_table.columnCount()):
            cell_item = self.aggregated_table.item(row, col)
            if cell_item:
                color = self._get_status_color(percentage)
                cell_item.setBackground(color)
    
    def sort_status_table(self, column_index):
        """Sort the status table by the specified column."""
        self.status_table.sortByColumn(column_index, Qt.AscendingOrder)
    
    def filter_status_table(self):
        """Filter the status table based on search input and criteria."""
        try:
            search_text = self.search_input_status.text().lower()
            filter_by = self.search_filter_combo_status.currentText()
            
            for row in range(self.status_table.rowCount()):
                match = False
                
                # Apply search filter based on criteria
                if search_text:
                    if filter_by == "All":
                        # Search in all columns
                        match = False
                        for col in range(3):  # Type, Color, Brand columns
                            cell = self.status_table.item(row, col)
                            if cell and search_text in cell.text().lower():
                                match = True
                                break
                    elif filter_by == "Type":
                        # Search only in Type column
                        cell = self.status_table.item(row, 0)
                        match = cell and search_text in cell.text().lower()
                    elif filter_by == "Color":
                        # Search only in Color column
                        cell = self.status_table.item(row, 1)
                        match = cell and search_text in cell.text().lower()
                    elif filter_by == "Brand":
                        # Search only in Brand column
                        cell = self.status_table.item(row, 2)
                        match = cell and search_text in cell.text().lower()
                else:
                    match = True
                
                self.status_table.setRowHidden(row, not match)
        except Exception as e:
            print(f"Error filtering status table: {str(e)}")
            # Don't hide any rows if there's an error
            for row in range(self.status_table.rowCount()):
                self.status_table.setRowHidden(row, False)

    def load_inventory_status(self):
        """Load inventory status comparison (current vs ideal)."""
        try:
            # Get inventory status data
            status_data = self.db_handler.get_inventory_status()
            
            if not status_data:
                # Clear the table if no status data
                self.status_table.setRowCount(0)
                return
                
            # Remember current sort settings
            sort_column = self.status_table.horizontalHeader().sortIndicatorSection()
            sort_order = self.status_table.horizontalHeader().sortIndicatorOrder()
            
            # Temporarily disable sorting to improve performance
            self.status_table.setSortingEnabled(False)
            
            # Clear table and set row count
            self.status_table.setRowCount(len(status_data))
            
            # Populate table with status data
            for row, item in enumerate(status_data):
                # Store row data for status coloring
                self.status_row_data = item
                
                # Type column (add prefix for groups)
                type_text = item['type']
                if item.get('is_group', False):
                    type_text = f"Group: {type_text}"
                self.status_table.setItem(row, 0, QTableWidgetItem(type_text))
                
                # Color column
                self.status_table.setItem(row, 1, QTableWidgetItem(item['color']))
                
                # Brand column
                self.status_table.setItem(row, 2, QTableWidgetItem(item['brand'] if 'brand' in item else ""))
                
                # Current quantity column
                current_item = QTableWidgetItem()
                current_item.setData(Qt.DisplayRole, float(item['current_quantity']))
                current_item.setText(f"{item['current_quantity']:.1f}")
                self.status_table.setItem(row, 3, current_item)
                
                # Ideal quantity column
                ideal_item = QTableWidgetItem()
                ideal_item.setData(Qt.DisplayRole, float(item['ideal_quantity']))
                ideal_item.setText(f"{item['ideal_quantity']:.1f}")
                self.status_table.setItem(row, 4, ideal_item)
                
                # Difference column
                difference = item['current_quantity'] - item['ideal_quantity']
                difference_item = QTableWidgetItem()
                difference_item.setData(Qt.DisplayRole, float(difference))
                difference_item.setText(f"{difference:.1f}")
                self.status_table.setItem(row, 5, difference_item)
                
                # Status column
                status_text = self._get_status_text(difference)
                status_item = QTableWidgetItem(status_text)
                self.status_table.setItem(row, 6, status_item)
                
                # Color code rows based on status
                self._apply_colors_to_status_row(row, difference)
            
            # Re-enable sorting and restore previous sort
            self.status_table.setSortingEnabled(True)
            if sort_column >= 0:
                self.status_table.sortByColumn(sort_column, sort_order)
                
            # Refresh filters after loading
            self.filter_status_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inventory status: {str(e)}")
    
    def _get_status_text(self, difference):
        """Get the status text based on the difference between current and ideal quantities."""
        if difference is None:
            return "No Target Set"
        
        # Calculate the percentage of current to ideal
        if 'ideal_quantity' in getattr(self, 'status_row_data', {}) and self.status_row_data['ideal_quantity'] > 0:
            ideal = self.status_row_data['ideal_quantity']
            current = self.status_row_data['current_quantity']
            percentage = (current / ideal) * 100
            
            if percentage == 0:
                return "Out of Stock"
            elif percentage < 20:
                return "Dangerous"
            elif percentage < 40:
                return "Critical"
            elif percentage < 60:
                return "Low"
            elif percentage < 80:
                return "Adequate"
            elif percentage <= 100:
                return "Optimal"
            else:
                return "Overstocked"
        else:
            return "No Target Set"
    
    def _apply_colors_to_status_row(self, row, difference):
        """Apply color coding to a status table row based on the difference."""
        # Get the current and ideal quantities from the status_row_data
        if not hasattr(self, 'status_row_data') or not self.status_row_data:
            return
            
        ideal_qty = self.status_row_data.get('ideal_quantity', 0)
        current_qty = self.status_row_data.get('current_quantity', 0)
        
        # Apply color to each cell in the row
        for col in range(self.status_table.columnCount()):
            cell_item = self.status_table.item(row, col)
            if cell_item:
                if ideal_qty == 0:
                    color = QColor(255, 255, 255)  # White for "No Ideal Target Set"
                else:
                    percentage = (current_qty / ideal_qty) * 100 if ideal_qty > 0 else 0
                    
                    if percentage == 0:
                        color = QColor(240, 240, 240)  # Light gray for "Out of Stock"
                    elif percentage < 20:
                        color = QColor(255, 200, 200)  # Light red for "Dangerous"
                    elif percentage < 40:
                        color = QColor(255, 235, 156)  # Light orange for "Critical"
                    elif percentage < 60:
                        color = QColor(255, 255, 200)  # Light yellow for "Low"
                    elif percentage < 80:
                        color = QColor(200, 235, 255)  # Light blue for "Adequate"
                    elif percentage <= 100:
                        color = QColor(200, 255, 200)  # Light green for "Optimal"
                    else:
                        color = QColor(230, 210, 255)  # Light purple for "Overstocked"
                
                cell_item.setBackground(color)
