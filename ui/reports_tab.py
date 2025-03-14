"""
Reports and data visualization tab interface.
"""
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QDateEdit, QGroupBox, QFormLayout,
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFrame, QSplitter, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPalette, QColor

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from database.db_handler import DatabaseHandler

class MplCanvas(FigureCanvas):
    """Matplotlib canvas for embedding charts in PyQt."""
    
    def __init__(self, width=5, height=4, dpi=100):
        """Initialize the canvas."""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.tight_layout()


class ReportsTab(QWidget):
    """Reports and data visualization tab."""
    
    def __init__(self, db_handler):
        """Initialize reports tab with database handler."""
        super().__init__()
        
        self.db_handler = db_handler
        
        # Track orientation state
        self.is_portrait = False
        
        self.setup_ui()
        
        # Initialize with the first tab selected
        self.tab_changed(0)
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        
        # Create tabs for different report types
        self.tab_widget = QTabWidget()
        
        # Usage summary tab
        self.usage_summary_tab = self.create_usage_summary_tab()
        self.tab_widget.addTab(self.usage_summary_tab, "Usage Summary")
        
        # Filament inventory tab
        self.filament_inventory_tab = self.create_filament_inventory_tab()
        self.tab_widget.addTab(self.filament_inventory_tab, "Filament Inventory")
        
        # Printer usage tab
        self.printer_usage_tab = self.create_printer_usage_tab()
        self.tab_widget.addTab(self.printer_usage_tab, "Printer Usage")
        
        # Cost analysis tab
        self.cost_analysis_tab = self.create_cost_analysis_tab()
        self.tab_widget.addTab(self.cost_analysis_tab, "Cost Analysis")
        
        # Component status tab
        self.component_status_tab = self.create_component_status_tab()
        self.tab_widget.addTab(self.component_status_tab, "Component Status")
        
        # Connect tab changed signal to refresh data
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        # Add tabs to main layout
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
        
    def tab_changed(self, index):
        """Handle tab changes to refresh data."""
        # Update electricity cost inputs if they exist
        global_cost = self.db_handler.get_electricity_cost()
        
        # Update cost display in all relevant tabs
        if hasattr(self, 'electricity_cost_input'):
            self.electricity_cost_input.setValue(global_cost)
        if hasattr(self, 'cost_electricity_input'):
            self.cost_electricity_input.setValue(global_cost)
        
        # Refresh data when tab is changed
        if index == 0:  # Usage Summary
            self.refresh_usage_summary()
        elif index == 1:  # Filament Inventory
            self.refresh_filament_inventory()
        elif index == 2:  # Printer Usage
            self.refresh_printer_usage()
        elif index == 3:  # Cost Analysis
            self.refresh_cost_analysis()
        elif index == 4:  # Component Status
            self.refresh_component_status()
    
    def create_usage_summary_tab(self):
        """Create the usage summary tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Controls for filtering and time range
        control_box = QGroupBox("Report Controls")
        controls_layout = QFormLayout()
        
        # Date range selection
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        self.start_date.setCalendarPopup(True)
        controls_layout.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())  # Default to today
        self.end_date.setCalendarPopup(True)
        controls_layout.addRow("End Date:", self.end_date)
        
        # Chart type selection
        self.chart_type = QComboBox()
        self.chart_type.addItems(["Filament Type", "Filament Color", "Filament Brand", "Printer", "Cost Analysis"])
        controls_layout.addRow("Group By:", self.chart_type)
        
        # Generate report button
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.refresh_usage_summary)
        controls_layout.addRow("", self.generate_button)
        
        control_box.setLayout(controls_layout)
        
        # Chart area
        self.usage_canvas = MplCanvas(width=8, height=4)
        
        # Create a frame for the canvas
        canvas_frame = QFrame()
        canvas_frame.setFrameShape(QFrame.StyledPanel)
        canvas_frame.setFrameShadow(QFrame.Sunken)
        canvas_layout = QVBoxLayout(canvas_frame)
        canvas_layout.addWidget(self.usage_canvas)
        
        # Summary statistics in a table
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels([
            "Category", "Filament Used (g)", "Percentage"
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Split the view with chart on top and table below
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(canvas_frame)
        splitter.addWidget(self.summary_table)
        splitter.setSizes([600, 200])  # Set initial sizes
        
        # Add widgets to layout
        layout.addWidget(control_box)
        layout.addWidget(splitter)
        
        tab.setLayout(layout)
        return tab
    
    def create_filament_inventory_tab(self):
        """Create the filament inventory tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Table showing current inventory
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            "Type", "Color", "Brand", "Remaining (g)", "Total (g)", "Percentage Remaining"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Create inventory canvas for chart
        self.inventory_canvas = MplCanvas(width=8, height=4)
        
        # Create a frame for the canvas
        canvas_frame = QFrame()
        canvas_frame.setFrameShape(QFrame.StyledPanel)
        canvas_frame.setFrameShadow(QFrame.Sunken)
        canvas_layout = QVBoxLayout(canvas_frame)
        canvas_layout.addWidget(self.inventory_canvas)
        
        # Controls for inventory view
        control_box = QGroupBox("Inventory View")
        controls_layout = QHBoxLayout()
        
        # Chart type selection
        self.inventory_view_type = QComboBox()
        self.inventory_view_type.addItems(["By Type", "By Color", "By Brand", "Low Stock Items"])
        self.inventory_view_type.currentIndexChanged.connect(self.refresh_filament_inventory)
        controls_layout.addWidget(QLabel("View:"))
        controls_layout.addWidget(self.inventory_view_type)
        
        # Refresh button
        self.inventory_refresh_button = QPushButton("Refresh")
        self.inventory_refresh_button.clicked.connect(self.refresh_filament_inventory)
        controls_layout.addWidget(self.inventory_refresh_button)
        
        controls_layout.addStretch()
        control_box.setLayout(controls_layout)
        
        # Add widgets to layout
        layout.addWidget(control_box)
        layout.addWidget(canvas_frame)
        layout.addWidget(self.inventory_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_printer_usage_tab(self):
        """Create the printer usage tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Controls for printer stats
        control_box = QGroupBox("Printer Statistics")
        controls_layout = QHBoxLayout()
        
        # Time period selection
        self.printer_time_period = QComboBox()
        self.printer_time_period.addItems(["All Time", "This Month", "This Year"])
        self.printer_time_period.currentIndexChanged.connect(self.refresh_printer_usage)
        controls_layout.addWidget(QLabel("Time Period:"))
        controls_layout.addWidget(self.printer_time_period)
        
        # Electricity cost per kWh (displays the global setting but allows temporary override)
        controls_layout.addWidget(QLabel("Electricity Cost per kWh:"))
        self.electricity_cost_input = QDoubleSpinBox()
        self.electricity_cost_input.setRange(0.01, 10.0)
        self.electricity_cost_input.setDecimals(2)
        self.electricity_cost_input.setValue(self.db_handler.get_electricity_cost())  # Use global setting
        self.electricity_cost_input.setSingleStep(0.01)
        self.electricity_cost_input.valueChanged.connect(self.refresh_printer_usage)
        controls_layout.addWidget(self.electricity_cost_input)
        
        # Refresh button
        self.printer_refresh_button = QPushButton("Refresh")
        self.printer_refresh_button.clicked.connect(self.refresh_printer_usage)
        controls_layout.addWidget(self.printer_refresh_button)
        
        controls_layout.addStretch()
        control_box.setLayout(controls_layout)
        
        # Create printer usage canvas
        self.printer_canvas = MplCanvas(width=8, height=4)
        
        # Create a frame for the canvas
        canvas_frame = QFrame()
        canvas_frame.setFrameShape(QFrame.StyledPanel)
        canvas_frame.setFrameShadow(QFrame.Sunken)
        canvas_layout = QVBoxLayout(canvas_frame)
        canvas_layout.addWidget(self.printer_canvas)
        
        # Table showing printer statistics
        self.printer_table = QTableWidget()
        self.printer_table.setColumnCount(5)
        self.printer_table.setHorizontalHeaderLabels([
            "Printer", "Total Jobs", "Total Hours", "Total Filament Used (g)", "Electricity Cost"
        ])
        self.printer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Add widgets to layout
        layout.addWidget(control_box)
        layout.addWidget(canvas_frame)
        layout.addWidget(self.printer_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_cost_analysis_tab(self):
        """Create the cost analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Controls for cost analysis
        control_box = QGroupBox("Cost Analysis Settings")
        controls_layout = QHBoxLayout()
        
        # Time period selection
        self.cost_time_period = QComboBox()
        self.cost_time_period.addItems(["All Time", "This Month", "This Year"])
        self.cost_time_period.currentIndexChanged.connect(self.refresh_cost_analysis)
        controls_layout.addWidget(QLabel("Time Period:"))
        controls_layout.addWidget(self.cost_time_period)
        
        # Electricity cost per kWh (displays the global setting but allows temporary override)
        controls_layout.addWidget(QLabel("Electricity Cost per kWh:"))
        self.cost_electricity_input = QDoubleSpinBox()
        self.cost_electricity_input.setRange(0.01, 10.0)
        self.cost_electricity_input.setDecimals(2)
        self.cost_electricity_input.setValue(self.db_handler.get_electricity_cost())  # Use global setting
        self.cost_electricity_input.setSingleStep(0.01)
        self.cost_electricity_input.valueChanged.connect(self.refresh_cost_analysis)
        controls_layout.addWidget(self.cost_electricity_input)
        
        # Grouping option
        controls_layout.addWidget(QLabel("Group By:"))
        self.cost_grouping = QComboBox()
        self.cost_grouping.addItems(["Project", "Filament Type", "Printer"])
        self.cost_grouping.currentIndexChanged.connect(self.refresh_cost_analysis)
        controls_layout.addWidget(self.cost_grouping)
        
        # Refresh button
        self.cost_refresh_button = QPushButton("Refresh")
        self.cost_refresh_button.clicked.connect(self.refresh_cost_analysis)
        controls_layout.addWidget(self.cost_refresh_button)
        
        controls_layout.addStretch()
        control_box.setLayout(controls_layout)
        
        # Create a splitter for charts and table
        splitter = QSplitter(Qt.Vertical)
        
        # Top part for charts
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)
        
        # Create two canvas frames side by side
        # Left chart - Cost breakdown (material vs electricity)
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setFrameShadow(QFrame.Sunken)
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("Cost Breakdown"))
        self.cost_breakdown_canvas = MplCanvas(width=5, height=4)
        left_layout.addWidget(self.cost_breakdown_canvas)
        
        # Right chart - Project/Filament/Printer comparison
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setFrameShadow(QFrame.Sunken)
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel("Cost Comparison"))
        self.cost_comparison_canvas = MplCanvas(width=5, height=4)
        right_layout.addWidget(self.cost_comparison_canvas)
        
        charts_layout.addWidget(left_frame)
        charts_layout.addWidget(right_frame)
        
        # Bottom part for detailed cost table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.addWidget(QLabel("Detailed Cost Breakdown"))
        
        self.cost_table = QTableWidget()
        self.cost_table.setColumnCount(6)
        self.cost_table.setHorizontalHeaderLabels([
            "Name", "Total Jobs", "Total Hours", "Material Cost", "Electricity Cost", "Total Cost"
        ])
        self.cost_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.cost_table)
        
        # Add widgets to splitter
        splitter.addWidget(charts_widget)
        splitter.addWidget(table_widget)
        
        # Add widgets to main layout
        layout.addWidget(control_box)
        layout.addWidget(splitter)
        
        tab.setLayout(layout)
        return tab
    
    def create_component_status_tab(self):
        """Create the component status tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Title and description
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("<h2>Printer Component Status</h2>"))
        title_layout.addStretch()
        
        description = QLabel("This report shows the status of printer components and their usage hours.")
        description.setWordWrap(True)
        
        # Table showing component status
        self.component_table = QTableWidget()
        self.component_table.setColumnCount(6)
        self.component_table.setHorizontalHeaderLabels([
            "Printer", "Component", "Installation Date", 
            "Usage (hours)", "Replacement Interval", "Status"
        ])
        self.component_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.component_refresh_button = QPushButton("Refresh")
        self.component_refresh_button.clicked.connect(self.refresh_component_status)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.component_refresh_button)
        
        # Add widgets to layout
        layout.addLayout(title_layout)
        layout.addWidget(description)
        layout.addWidget(self.component_table)
        layout.addLayout(refresh_layout)
        
        tab.setLayout(layout)
        return tab
    
    def refresh_usage_summary(self):
        """Refresh the usage summary chart and table."""
        try:
            # Get selected parameters
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            chart_type = self.chart_type.currentText()
            
            # Get print jobs within date range
            print_jobs = self.db_handler.get_print_jobs(
                start_date=start_date,
                end_date=end_date
            )
            
            if not print_jobs:
                # Clear and display no data message
                self.usage_canvas.axes.clear()
                self.usage_canvas.axes.text(0.5, 0.5, 'No data available for the selected period', 
                                          ha='center', va='center')
                self.usage_canvas.draw()
                self.summary_table.setRowCount(0)
                return
            
            # Process data based on chart type
            data = {}
            total_used = 0
            total_cost = 0
            
            for job in print_jobs:
                total_used += job.filament_used
                
                # Calculate cost if filament price is available
                job_cost = 0
                if job.filament.price is not None:
                    # Calculate cost based on price per kg
                    job_cost = (job.filament.price / job.filament.spool_weight) * job.filament_used
                    total_cost += job_cost
                
                if chart_type == "Filament Type":
                    key = job.filament.type
                    if key in data:
                        data[key] += job.filament_used
                    else:
                        data[key] = job.filament_used
                elif chart_type == "Filament Color":
                    key = job.filament.color
                    if key in data:
                        data[key] += job.filament_used
                    else:
                        data[key] = job.filament_used
                elif chart_type == "Filament Brand":
                    key = job.filament.brand
                    if key in data:
                        data[key] += job.filament_used
                    else:
                        data[key] = job.filament_used
                elif chart_type == "Printer":
                    key = job.printer.name
                    if key in data:
                        data[key] += job.filament_used
                    else:
                        data[key] = job.filament_used
                elif chart_type == "Cost Analysis":
                    key = job.filament.type
                    if job.filament.price is not None:
                        if key in data:
                            data[key] += job_cost
                        else:
                            data[key] = job_cost
                else:
                    key = "Unknown"
                    if key in data:
                        data[key] += job.filament_used
                    else:
                        data[key] = job.filament_used
            
            # Sort data for better visualization
            sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
            
            # Create chart
            self.usage_canvas.axes.clear()
            x = range(len(sorted_data))
            bars = self.usage_canvas.axes.bar(x, sorted_data.values(), 
                                           color=plt.cm.viridis(np.linspace(0, 1, len(sorted_data))))
            
            self.usage_canvas.axes.set_xticks(x)
            self.usage_canvas.axes.set_xticklabels(sorted_data.keys(), rotation=45, ha='right')
            
            # Set appropriate labels based on chart type
            if chart_type == "Cost Analysis":
                self.usage_canvas.axes.set_ylabel('Cost (Currency)')
                self.usage_canvas.axes.set_title(f'Filament Cost by {chart_type.replace("Cost Analysis", "Type")}')
                
                # Add cost labels on bars
                for bar in bars:
                    height = bar.get_height()
                    self.usage_canvas.axes.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                             f'${height:.2f}', ha='center', va='bottom', rotation=0)
            else:
                self.usage_canvas.axes.set_ylabel('Filament Used (g)')
                self.usage_canvas.axes.set_title(f'Filament Usage by {chart_type}')
                
                # Add data labels on bars
                for bar in bars:
                    height = bar.get_height()
                    self.usage_canvas.axes.text(bar.get_x() + bar.get_width()/2., height + 5,
                                             f'{height:.1f}g', ha='center', va='bottom', rotation=0)
            
            self.usage_canvas.fig.tight_layout()
            self.usage_canvas.draw()
            
            # Update summary table
            self.summary_table.setRowCount(len(sorted_data) + 1)  # +1 for total row
            
            for i, (category, amount) in enumerate(sorted_data.items()):
                # Set category name
                self.summary_table.setItem(i, 0, QTableWidgetItem(category))
                
                # Set amount (filament or cost)
                if chart_type == "Cost Analysis":
                    self.summary_table.setItem(i, 1, QTableWidgetItem(f"${amount:.2f}"))
                    percentage = (amount / total_cost * 100) if total_cost > 0 else 0
                else:
                    self.summary_table.setItem(i, 1, QTableWidgetItem(f"{amount:.1f}g"))
                    percentage = (amount / total_used * 100) if total_used > 0 else 0
                
                # Set percentage
                self.summary_table.setItem(i, 2, QTableWidgetItem(f"{percentage:.1f}%"))
            
            # Add total row
            total_row = len(sorted_data)
            self.summary_table.setItem(total_row, 0, QTableWidgetItem("TOTAL"))
            
            if chart_type == "Cost Analysis":
                self.summary_table.setItem(total_row, 1, QTableWidgetItem(f"${total_cost:.2f}"))
            else:
                self.summary_table.setItem(total_row, 1, QTableWidgetItem(f"{total_used:.1f}g"))
            
            self.summary_table.setItem(total_row, 2, QTableWidgetItem("100.0%"))
            
            # Highlight the total row
            for col in range(3):
                if self.summary_table.item(total_row, col):
                    self.summary_table.item(total_row, col).setBackground(QColor(230, 230, 230))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate usage summary: {str(e)}")
    
    def refresh_filament_inventory(self):
        """Refresh the filament inventory display."""
        try:
            view_type = self.inventory_view_type.currentText()
            filaments = self.db_handler.get_filaments()
            
            if not filaments:
                # Clear and display no data message
                self.inventory_canvas.axes.clear()
                self.inventory_canvas.axes.text(0.5, 0.5, 'No filament data available', 
                                             ha='center', va='center')
                self.inventory_canvas.draw()
                self.inventory_table.setRowCount(0)
                return
            
            # Process data for table
            self.inventory_table.setRowCount(len(filaments))
            
            for i, filament in enumerate(filaments):
                percentage = (filament.quantity_remaining / filament.spool_weight * 100) if filament.spool_weight > 0 else 0
                
                self.inventory_table.setItem(i, 0, QTableWidgetItem(filament.type))
                self.inventory_table.setItem(i, 1, QTableWidgetItem(filament.color))
                self.inventory_table.setItem(i, 2, QTableWidgetItem(filament.brand))
                self.inventory_table.setItem(i, 3, QTableWidgetItem(f"{filament.quantity_remaining:.1f}"))
                self.inventory_table.setItem(i, 4, QTableWidgetItem(f"{filament.spool_weight:.1f}"))
                self.inventory_table.setItem(i, 5, QTableWidgetItem(f"{percentage:.1f}%"))
                
                # Color code low filament
                if percentage < 20:
                    for col in range(6):
                        self.inventory_table.item(i, col).setBackground(QColor(255, 200, 200))
            
            # Process data for chart based on view type
            self.inventory_canvas.axes.clear()
            
            if view_type == "By Type":
                # Group by filament type
                data = {}
                for filament in filaments:
                    if filament.type in data:
                        data[filament.type] += filament.quantity_remaining
                    else:
                        data[filament.type] = filament.quantity_remaining
                
                # Create pie chart
                labels = data.keys()
                sizes = data.values()
                
                self.inventory_canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           startangle=90, shadow=False)
                self.inventory_canvas.axes.axis('equal')
                self.inventory_canvas.axes.set_title('Filament Inventory by Type')
                
            elif view_type == "By Color":
                # Group by color
                data = {}
                for filament in filaments:
                    if filament.color in data:
                        data[filament.color] += filament.quantity_remaining
                    else:
                        data[filament.color] = filament.quantity_remaining
                
                # Create pie chart
                labels = data.keys()
                sizes = data.values()
                
                self.inventory_canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           startangle=90, shadow=False)
                self.inventory_canvas.axes.axis('equal')
                self.inventory_canvas.axes.set_title('Filament Inventory by Color')
                
            elif view_type == "By Brand":
                # Group by brand
                data = {}
                for filament in filaments:
                    if filament.brand in data:
                        data[filament.brand] += filament.quantity_remaining
                    else:
                        data[filament.brand] = filament.quantity_remaining
                
                # Create pie chart
                labels = data.keys()
                sizes = data.values()
                
                self.inventory_canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           startangle=90, shadow=False)
                self.inventory_canvas.axes.axis('equal')
                self.inventory_canvas.axes.set_title('Filament Inventory by Brand')
                
            elif view_type == "Low Stock Items":
                # Filter low stock items (less than 20% remaining)
                low_stock = [f for f in filaments if f.quantity_remaining / f.spool_weight < 0.2]
                
                if not low_stock:
                    self.inventory_canvas.axes.text(0.5, 0.5, 'No low stock items', 
                                                 ha='center', va='center')
                else:
                    # Create bar chart of low stock items
                    names = [f"{f.brand} {f.color} {f.type}" for f in low_stock]
                    percentages = [(f.quantity_remaining / f.spool_weight * 100) for f in low_stock]
                    
                    y_pos = range(len(names))
                    bars = self.inventory_canvas.axes.barh(y_pos, percentages, color='red')
                    self.inventory_canvas.axes.set_yticks(y_pos)
                    self.inventory_canvas.axes.set_yticklabels(names)
                    self.inventory_canvas.axes.set_xlabel('Percentage Remaining')
                    self.inventory_canvas.axes.set_title('Low Stock Filaments (< 20%)')
                    
                    # Add data labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        self.inventory_canvas.axes.text(max(width + 1, 5), bar.get_y() + bar.get_height()/2,
                                                     f"{width:.1f}% ({low_stock[i].quantity_remaining:.0f}g)",
                                                     ha='left', va='center')
                    
                    self.inventory_canvas.axes.set_xlim(0, 20)  # Set limit to 20%
            
            self.inventory_canvas.fig.tight_layout()
            self.inventory_canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate inventory report: {str(e)}")
    
    def refresh_printer_usage(self):
        """Refresh the printer usage stats."""
        try:
            # Get settings
            time_period = self.printer_time_period.currentText()
            electricity_cost_per_kwh = self.electricity_cost_input.value()
            
            # Update electricity cost from global setting if it has changed
            global_cost = self.db_handler.get_electricity_cost()
            if abs(electricity_cost_per_kwh - global_cost) < 0.001:  # If they match within a small epsilon
                # Update to exactly match the global value to avoid floating point issues
                self.electricity_cost_input.setValue(global_cost)
            
            # Determine date range based on selection
            end_date = datetime.datetime.now()
            if time_period == "This Month":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time_period == "This Year":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # All Time
                start_date = None
            
            # Get print jobs within date range
            print_jobs = self.db_handler.get_print_jobs(
                start_date=start_date,
                end_date=end_date
            )
            
            if not print_jobs:
                # Clear and display no data message
                self.printer_canvas.axes.clear()
                self.printer_canvas.axes.text(0.5, 0.5, 'No print job data available for the selected period', 
                                          ha='center', va='center')
                self.printer_canvas.draw()
                self.printer_table.setRowCount(0)
                return
            
            # Process printer usage data
            printer_data = {}
            
            for job in print_jobs:
                printer_name = job.printer.name
                
                if printer_name not in printer_data:
                    printer_data[printer_name] = {
                        'total_jobs': 0,
                        'total_hours': 0,
                        'total_filament': 0,
                        'electricity_cost': 0
                    }
                
                printer_data[printer_name]['total_jobs'] += 1
                printer_data[printer_name]['total_hours'] += job.duration
                printer_data[printer_name]['total_filament'] += job.filament_used
                
                # Calculate electricity cost
                if hasattr(job.printer, 'power_consumption') and job.printer.power_consumption > 0:
                    electricity_cost = job.printer.power_consumption * job.duration * electricity_cost_per_kwh
                    printer_data[printer_name]['electricity_cost'] += electricity_cost
            
            # Create chart with multiple metrics
            printer_names = list(printer_data.keys())
            x = range(len(printer_names))
            
            # Create a new chart directly on our canvas instead of copying from another figure
            self.printer_canvas.axes.clear()
            width = 0.25  # Narrower width to accommodate three bars
            
            # Bar for filament used
            filament_bars = self.printer_canvas.axes.bar(
                [i - width for i in x], 
                [data['total_filament'] for data in printer_data.values()], 
                width, 
                label='Filament Used (g)', 
                color='dodgerblue'
            )
            
            # Create a second y-axis for print hours
            ax2 = self.printer_canvas.axes.twinx()
            hours_bars = ax2.bar(
                [i for i in x], 
                [data['total_hours'] for data in printer_data.values()], 
                width, 
                label='Print Hours', 
                color='orange'
            )
            
            # Create a third bar for electricity cost
            cost_bars = ax2.bar(
                [i + width for i in x], 
                [data['electricity_cost'] for data in printer_data.values()], 
                width, 
                label='Electricity Cost ($)', 
                color='green'
            )
            
            # Set labels and title
            self.printer_canvas.axes.set_xlabel('Printer')
            self.printer_canvas.axes.set_ylabel('Filament Used (g)')
            self.printer_canvas.axes.set_title(f'Printer Usage Statistics ({time_period})')
            self.printer_canvas.axes.set_xticks(x)
            self.printer_canvas.axes.set_xticklabels(printer_names)
            ax2.set_ylabel('Print Hours / Cost ($)')
            
            # Add legend
            lines1, labels1 = self.printer_canvas.axes.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            self.printer_canvas.axes.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Add data labels
            for i, bar in enumerate(filament_bars):
                height = bar.get_height()
                self.printer_canvas.axes.annotate(
                    f'{height:.0f}g',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', 
                    va='bottom'
                )
            
            for i, bar in enumerate(hours_bars):
                height = bar.get_height()
                ax2.annotate(
                    f'{height:.1f}h',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', 
                    va='bottom'
                )
                
            for i, bar in enumerate(cost_bars):
                height = bar.get_height()
                ax2.annotate(
                    f'${height:.2f}',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', 
                    va='bottom'
                )
            
            # Apply tight layout and redraw
            self.printer_canvas.fig.tight_layout()
            self.printer_canvas.draw()
            
            # Update table
            self.printer_table.setRowCount(len(printer_data))
            
            for i, (printer, data) in enumerate(printer_data.items()):
                self.printer_table.setItem(i, 0, QTableWidgetItem(printer))
                self.printer_table.setItem(i, 1, QTableWidgetItem(str(data['total_jobs'])))
                self.printer_table.setItem(i, 2, QTableWidgetItem(f"{data['total_hours']:.1f}"))
                self.printer_table.setItem(i, 3, QTableWidgetItem(f"{data['total_filament']:.1f}"))
                self.printer_table.setItem(i, 4, QTableWidgetItem(f"${data['electricity_cost']:.2f}"))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate printer usage report: {str(e)}")
    
    def refresh_component_status(self):
        """Refresh the component status display."""
        try:
            components = self.db_handler.get_printer_components()
            
            if not components:
                self.component_table.setRowCount(0)
                return
            
            # Process component data
            self.component_table.setRowCount(len(components))
            
            for i, component in enumerate(components):
                # Printer name
                self.component_table.setItem(i, 0, QTableWidgetItem(component.printer.name))
                
                # Component name
                self.component_table.setItem(i, 1, QTableWidgetItem(component.name))
                
                # Installation date
                date_str = component.installation_date.strftime("%Y-%m-%d") if component.installation_date else "N/A"
                self.component_table.setItem(i, 2, QTableWidgetItem(date_str))
                
                # Usage hours
                self.component_table.setItem(i, 3, QTableWidgetItem(f"{component.usage_hours:.1f}"))
                
                # Replacement interval
                interval_text = f"{component.replacement_interval}" if component.replacement_interval else "N/A"
                self.component_table.setItem(i, 4, QTableWidgetItem(interval_text))
                
                # Status
                if component.replacement_interval is None:
                    status = "Unknown"
                    status_color = QColor(200, 200, 200)  # Gray
                elif component.usage_hours >= component.replacement_interval:
                    status = "Replace Now"
                    status_color = QColor(255, 100, 100)  # Red
                elif component.usage_hours >= component.replacement_interval * 0.8:
                    status = "Replace Soon"
                    status_color = QColor(255, 180, 100)  # Orange
                else:
                    remaining = component.replacement_interval - component.usage_hours
                    percent = (component.usage_hours / component.replacement_interval) * 100
                    status = f"OK ({percent:.0f}% used)"
                    status_color = QColor(100, 255, 100)  # Green
                
                status_item = QTableWidgetItem(status)
                status_item.setBackground(status_color)
                self.component_table.setItem(i, 5, status_item)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load component status: {str(e)}")
    
    def refresh_cost_analysis(self):
        """Refresh the cost analysis displays."""
        try:
            # Get settings
            time_period = self.cost_time_period.currentText()
            electricity_cost_per_kwh = self.cost_electricity_input.value()
            grouping = self.cost_grouping.currentText()
            
            # Update electricity cost from global setting if it has changed
            global_cost = self.db_handler.get_electricity_cost()
            if abs(electricity_cost_per_kwh - global_cost) < 0.001:  # If they match within a small epsilon
                # Update to exactly match the global value to avoid floating point issues
                self.cost_electricity_input.setValue(global_cost)
            
            # Determine date range based on selection
            end_date = datetime.datetime.now()
            if time_period == "This Month":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time_period == "This Year":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # All Time
                start_date = None
            
            # Get print jobs within date range
            print_jobs = self.db_handler.get_print_jobs(
                start_date=start_date,
                end_date=end_date
            )
            
            if not print_jobs:
                # Clear and display no data message
                self.cost_breakdown_canvas.axes.clear()
                self.cost_breakdown_canvas.axes.text(0.5, 0.5, 'No print job data available for the selected period', 
                                               ha='center', va='center')
                self.cost_breakdown_canvas.draw()
                
                self.cost_comparison_canvas.axes.clear()
                self.cost_comparison_canvas.axes.text(0.5, 0.5, 'No print job data available for the selected period', 
                                                ha='center', va='center')
                self.cost_comparison_canvas.draw()
                
                self.cost_table.setRowCount(0)
                return
            
            # Initialize aggregation data
            total_material_cost = 0
            total_electricity_cost = 0
            grouped_data = {}
            
            # Process job data
            for job in print_jobs:
                # Calculate material cost
                material_cost = 0
                
                # Primary filament cost
                if job.filament and job.filament.price is not None and job.filament.spool_weight:
                    cost_per_gram = job.filament.price / job.filament.spool_weight
                    material_cost += cost_per_gram * job.filament_used
                
                # Secondary filaments
                if job.filament_id_2 and job.filament_2 and job.filament_2.price is not None and job.filament_2.spool_weight:
                    cost_per_gram = job.filament_2.price / job.filament_2.spool_weight
                    material_cost += cost_per_gram * job.filament_used_2
                
                if job.filament_id_3 and job.filament_3 and job.filament_3.price is not None and job.filament_3.spool_weight:
                    cost_per_gram = job.filament_3.price / job.filament_3.spool_weight
                    material_cost += cost_per_gram * job.filament_used_3
                
                if job.filament_id_4 and job.filament_4 and job.filament_4.price is not None and job.filament_4.spool_weight:
                    cost_per_gram = job.filament_4.price / job.filament_4.spool_weight
                    material_cost += cost_per_gram * job.filament_used_4
                
                # Calculate electricity cost
                electricity_cost = 0
                if hasattr(job.printer, 'power_consumption') and job.printer.power_consumption > 0:
                    electricity_cost = job.printer.power_consumption * job.duration * electricity_cost_per_kwh
                
                # Update totals
                total_material_cost += material_cost
                total_electricity_cost += electricity_cost
                
                # Group data based on selected grouping
                if grouping == "Project":
                    group_key = job.project_name
                elif grouping == "Filament Type":
                    group_key = f"{job.filament.type}"
                else:  # Printer
                    group_key = job.printer.name
                
                if group_key not in grouped_data:
                    grouped_data[group_key] = {
                        'total_jobs': 0,
                        'total_hours': 0,
                        'material_cost': 0,
                        'electricity_cost': 0
                    }
                
                grouped_data[group_key]['total_jobs'] += 1
                grouped_data[group_key]['total_hours'] += job.duration
                grouped_data[group_key]['material_cost'] += material_cost
                grouped_data[group_key]['electricity_cost'] += electricity_cost
            
            # Create overall cost breakdown pie chart
            self.cost_breakdown_canvas.axes.clear()
            
            # Only create pie chart if there are costs
            if total_material_cost > 0 or total_electricity_cost > 0:
                labels = ['Material Cost', 'Electricity Cost']
                sizes = [total_material_cost, total_electricity_cost]
                colors = ['#ff9999', '#66b3ff']
                
                self.cost_breakdown_canvas.axes.pie(
                    sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                    startangle=90, shadow=False
                )
                self.cost_breakdown_canvas.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                self.cost_breakdown_canvas.axes.set_title(f'Cost Breakdown ({time_period})\nTotal: ${total_material_cost + total_electricity_cost:.2f}')
            else:
                self.cost_breakdown_canvas.axes.text(0.5, 0.5, 'No cost data available', ha='center', va='center')
            
            self.cost_breakdown_canvas.draw()
            
            # Create grouped cost comparison chart
            self.cost_comparison_canvas.axes.clear()
            
            if grouped_data:
                group_names = list(grouped_data.keys())
                x = range(len(group_names))
                width = 0.35
                
                # Bar for material cost
                material_bars = self.cost_comparison_canvas.axes.bar(
                    [i - width/2 for i in x], 
                    [data['material_cost'] for data in grouped_data.values()], 
                    width, 
                    label='Material Cost', 
                    color='#ff9999'
                )
                
                # Bar for electricity cost
                electricity_bars = self.cost_comparison_canvas.axes.bar(
                    [i + width/2 for i in x], 
                    [data['electricity_cost'] for data in grouped_data.values()], 
                    width, 
                    label='Electricity Cost', 
                    color='#66b3ff'
                )
                
                # Set labels and title
                self.cost_comparison_canvas.axes.set_xlabel(f'{grouping}')
                self.cost_comparison_canvas.axes.set_ylabel('Cost ($)')
                self.cost_comparison_canvas.axes.set_title(f'Cost Comparison by {grouping}')
                self.cost_comparison_canvas.axes.set_xticks(x)
                
                # Format x-tick labels to fit
                if len(max(group_names, key=len)) > 10:
                    self.cost_comparison_canvas.axes.set_xticklabels(
                        group_names, rotation=45, ha='right'
                    )
                else:
                    self.cost_comparison_canvas.axes.set_xticklabels(group_names)
                
                # Add legend
                self.cost_comparison_canvas.axes.legend()
                
                # Add data labels
                for i, bar in enumerate(material_bars):
                    height = bar.get_height()
                    if height > 0:
                        self.cost_comparison_canvas.axes.annotate(
                            f'${height:.2f}',
                            xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', 
                            va='bottom'
                        )
                
                for i, bar in enumerate(electricity_bars):
                    height = bar.get_height()
                    if height > 0:
                        self.cost_comparison_canvas.axes.annotate(
                            f'${height:.2f}',
                            xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', 
                            va='bottom'
                        )
            else:
                self.cost_comparison_canvas.axes.text(0.5, 0.5, 'No cost data available', ha='center', va='center')
            
            self.cost_comparison_canvas.fig.tight_layout()
            self.cost_comparison_canvas.draw()
            
            # Update table
            self.cost_table.setRowCount(len(grouped_data))
            
            for i, (name, data) in enumerate(grouped_data.items()):
                total_cost = data['material_cost'] + data['electricity_cost']
                
                self.cost_table.setItem(i, 0, QTableWidgetItem(name))
                self.cost_table.setItem(i, 1, QTableWidgetItem(str(data['total_jobs'])))
                self.cost_table.setItem(i, 2, QTableWidgetItem(f"{data['total_hours']:.1f}"))
                self.cost_table.setItem(i, 3, QTableWidgetItem(f"${data['material_cost']:.2f}"))
                self.cost_table.setItem(i, 4, QTableWidgetItem(f"${data['electricity_cost']:.2f}"))
                self.cost_table.setItem(i, 5, QTableWidgetItem(f"${total_cost:.2f}"))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate cost analysis report: {str(e)}")

    def adjust_for_portrait(self, is_portrait):
        """Adjust the layout based on screen orientation."""
        self.is_portrait = is_portrait
        
        if is_portrait:
            # Vertical monitor adjustments
            
            # Change tab orientation if subtabs exist
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setTabPosition(QTabWidget.West)  # Tabs on the left in portrait
            elif hasattr(self, 'tabs'):
                self.tabs.setTabPosition(QTabWidget.West)  # Tabs on the left in portrait
            
            # Adjust any splitters to vertical orientation
            if hasattr(self, 'summary_splitter'):
                self.summary_splitter.setOrientation(Qt.Vertical)
            
            # Optimize report table column widths
            for table_attr in ['summary_table', 'inventory_table', 'printer_table', 'cost_table',
                              'filament_usage_table', 'printer_usage_table']:
                if hasattr(self, table_attr):
                    table = getattr(self, table_attr)
                    header = table.horizontalHeader()
                    header.resizeSections(QHeaderView.ResizeToContents)
                    
                    # Make ID columns narrower
                    if table.columnCount() > 0:
                        header.setSectionResizeMode(0, QHeaderView.Fixed)
                        header.resizeSection(0, 40)  # ID column
                    
                    # Make date columns fixed width
                    for i in range(table.columnCount()):
                        if table.horizontalHeaderItem(i) and "Date" in table.horizontalHeaderItem(i).text():
                            header.setSectionResizeMode(i, QHeaderView.Fixed)
                            header.resizeSection(i, 80)
                    
                    # Make numeric columns narrower
                    for i in range(table.columnCount()):
                        if table.horizontalHeaderItem(i) and any(term in table.horizontalHeaderItem(i).text() for term in ["Amount", "Cost", "Weight", "Price", "Quantity", "Usage"]):
                            header.setSectionResizeMode(i, QHeaderView.Fixed)
                            header.resizeSection(i, 70)
            
            # Collapse control panels to save vertical space
            for panel_attr in ['controls_group', 'filter_group', 'date_filter_group']:
                if hasattr(self, panel_attr):
                    panel = getattr(self, panel_attr)
                    panel.setMaximumHeight(150)
                    
        else:
            # Reset to landscape mode (horizontal monitor)
            
            # Reset tab orientation
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setTabPosition(QTabWidget.North)  # Tabs on top in landscape
            elif hasattr(self, 'tabs'): 
                self.tabs.setTabPosition(QTabWidget.North)  # Tabs on top in landscape
                
            # Reset splitter orientation
            if hasattr(self, 'summary_splitter'):
                self.summary_splitter.setOrientation(Qt.Vertical)  # Usually vertical even in landscape
            
            # Reset table columns to default
            for table_attr in ['summary_table', 'inventory_table', 'printer_table', 'cost_table',
                              'filament_usage_table', 'printer_usage_table']:
                if hasattr(self, table_attr):
                    table = getattr(self, table_attr)
                    header = table.horizontalHeader()
                    for i in range(table.columnCount()):
                        header.setSectionResizeMode(i, QHeaderView.Interactive)
                    header.resizeSections(QHeaderView.ResizeToContents)
            
            # Reset collapsed panels
            for panel_attr in ['controls_group', 'filter_group', 'date_filter_group']:
                if hasattr(self, panel_attr):
                    panel = getattr(self, panel_attr)
                    panel.setMaximumHeight(16777215)  # Default/unlimited
                    