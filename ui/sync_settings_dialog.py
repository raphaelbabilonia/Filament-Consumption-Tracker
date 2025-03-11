"""
Dialog for configuring cloud synchronization settings.
"""
import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QCheckBox, QGroupBox, QSpinBox,
                            QDialogButtonBox, QComboBox, QFormLayout)
from PyQt5.QtCore import Qt

class SyncSettingsDialog(QDialog):
    """Dialog for configuring cloud synchronization settings."""
    
    def __init__(self, parent=None):
        """Initialize the sync settings dialog."""
        super().__init__(parent)
        
        self.parent = parent
        self.settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'database', 'sync_settings.json')
        self.settings = self.load_settings()
        
        # Setup UI
        self.setWindowTitle("Cloud Sync Settings")
        self.setMinimumSize(500, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI components."""
        main_layout = QVBoxLayout()
        
        # Auto-sync group
        auto_sync_group = QGroupBox("Automatic Synchronization")
        auto_sync_layout = QVBoxLayout()
        
        self.enable_auto_sync = QCheckBox("Enable automatic synchronization")
        self.enable_auto_sync.setChecked(self.settings.get("auto_sync_enabled", False))
        
        sync_options_layout = QFormLayout()
        
        # Sync frequency
        self.sync_frequency = QComboBox()
        self.sync_frequency.addItems(["On application close", "Daily", "Hourly"])
        self.sync_frequency.setCurrentText(self.settings.get("sync_frequency", "On application close"))
        sync_options_layout.addRow("Sync frequency:", self.sync_frequency)
        
        # Maximum backup files to keep
        self.max_backups = QSpinBox()
        self.max_backups.setRange(1, 50)
        self.max_backups.setValue(self.settings.get("max_backups", 5))
        sync_options_layout.addRow("Maximum backups to keep:", self.max_backups)
        
        auto_sync_layout.addWidget(self.enable_auto_sync)
        auto_sync_layout.addLayout(sync_options_layout)
        auto_sync_group.setLayout(auto_sync_layout)
        
        # Sync status group
        sync_status_group = QGroupBox("Sync Status")
        sync_status_layout = QFormLayout()
        
        self.last_sync_label = QLabel(self.settings.get("last_sync", "Never"))
        sync_status_layout.addRow("Last sync:", self.last_sync_label)
        
        sync_now_btn = QPushButton("Sync Now")
        sync_now_btn.clicked.connect(self.sync_now)
        
        sync_status_layout.addRow("", sync_now_btn)
        sync_status_group.setLayout(sync_status_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        
        main_layout.addWidget(auto_sync_group)
        main_layout.addWidget(sync_status_group)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
    def load_settings(self):
        """Load synchronization settings from file."""
        default_settings = {
            "auto_sync_enabled": False,
            "sync_frequency": "On application close",
            "max_backups": 5,
            "last_sync": "Never"
        }
        
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return default_settings
        return default_settings
        
    def save_settings(self):
        """Save synchronization settings to file."""
        settings = {
            "auto_sync_enabled": self.enable_auto_sync.isChecked(),
            "sync_frequency": self.sync_frequency.currentText(),
            "max_backups": self.max_backups.value(),
            "last_sync": self.settings.get("last_sync", "Never")
        }
        
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            self.settings = settings
            self.accept()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not save settings: {str(e)}")
            
    def sync_now(self):
        """Trigger an immediate synchronization."""
        if self.parent and hasattr(self.parent, 'backup_to_drive'):
            # Update last sync time
            from datetime import datetime
            self.settings["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_sync_label.setText(self.settings["last_sync"])
            
            # Save settings
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
                
            # Call parent's backup method
            self.parent.backup_to_drive()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Could not initiate sync - parent window not available.") 