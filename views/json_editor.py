from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QFileDialog,
    QTextEdit, QSplitter, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt
import json
import os
import shutil
from config import PROJECTS_DB_DIR
from utils.debug import debug_print

class JsonEditorDialog(QDialog):
    def __init__(self, parent=None, file_path=None, project=None):
        super().__init__(parent)
        self.file_path = file_path
        self.json_data = {}
        self.parent_key = None  # For handling one level of nesting
        self.project = project  # Reference to the project object
        
        self.setup_ui()
        
        if file_path and os.path.exists(file_path):
            self.load_json_file(file_path)
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("JSON Editor")
        self.resize(600, 500)  # Make the dialog larger by default
        
        layout = QVBoxLayout(self)
        
        # File info header
        self.file_label = QLabel("No file loaded")
        layout.addWidget(self.file_label)
        
        # Add checkbox for syncing to project
        self.sync_checkbox = QCheckBox("Save to project directory (will be overwritten on next edit)")
        self.sync_checkbox.setChecked(True)
        layout.addWidget(self.sync_checkbox)
        
        # Create a splitter to allow resizing between table and value editor
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Table widget container
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table for key-value pairs
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Key", "Value"])
        
        # Set key column to fixed width and value column to take remaining space
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 150)  # Fixed width for key column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Allow cells to expand vertically to show more content
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Connect selection change to update the value editor
        self.table.itemSelectionChanged.connect(self.update_value_editor)
        
        table_layout.addWidget(self.table)
        splitter.addWidget(table_widget)
        
        # Value editor for more comfortable editing of long values
        value_editor_widget = QWidget()
        value_editor_layout = QVBoxLayout(value_editor_widget)
        value_editor_layout.setContentsMargins(0, 0, 0, 0)
        
        value_editor_label = QLabel("Value Editor:")
        value_editor_layout.addWidget(value_editor_label)
        
        self.value_editor = QTextEdit()
        self.value_editor.setPlaceholderText("Select a row to edit its value here")
        self.value_editor.textChanged.connect(self.update_selected_value)
        value_editor_layout.addWidget(self.value_editor)
        
        splitter.addWidget(value_editor_widget)
        
        # Set initial sizes for the splitter (70% table, 30% value editor)
        splitter.setSizes([350, 150])
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Row")
        self.add_button.clicked.connect(self.add_row)
        button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_row)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_json)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_value_editor(self):
        """Update the value editor with the selected row's value"""
        selected_items = self.table.selectedItems()
        
        # Clear the editor if no selection or multiple rows selected
        if not selected_items:
            self.value_editor.clear()
            self.value_editor.setEnabled(False)
            return
        
        # Get the selected row and its value
        row = selected_items[0].row()
        value_item = self.table.item(row, 1)
        
        if value_item:
            self.value_editor.setEnabled(True)
            # Disconnect signal temporarily to prevent recursion
            self.value_editor.textChanged.disconnect(self.update_selected_value)
            self.value_editor.setText(value_item.text())
            self.value_editor.textChanged.connect(self.update_selected_value)
    
    def update_selected_value(self):
        """Update the selected table cell with the value from the editor"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        value_item = self.table.item(row, 1)
        
        if value_item:
            value_item.setText(self.value_editor.toPlainText())
    
    def load_json_file(self, file_path):
        """Load JSON data from a file"""
        try:
            with open(file_path, 'r') as f:
                self.json_data = json.load(f)
            
            self.file_path = file_path
            self.file_label.setText(f"Editing: {os.path.basename(file_path)}")
            
            # Detect if we have a single parent key (one level of nesting)
            if len(self.json_data) == 1 and isinstance(list(self.json_data.values())[0], dict):
                self.parent_key = list(self.json_data.keys())[0]
                self.populate_table(self.json_data[self.parent_key])
            else:
                self.parent_key = None
                self.populate_table(self.json_data)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file: {str(e)}")
    
    def populate_table(self, data):
        """Populate the table with key-value pairs"""
        self.table.setRowCount(0)  # Clear existing rows
        
        for key, value in data.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Add key item (non-editable)
            key_item = QTableWidgetItem(key)
            self.table.setItem(row, 0, key_item)
            
            # Add value item
            value_str = value if isinstance(value, str) else json.dumps(value)
            value_item = QTableWidgetItem(value_str)
            # Allow text to wrap in cells
            value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, value_item)
    
    def add_row(self):
        """Add a new empty row to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Add default items
        self.table.setItem(row, 0, QTableWidgetItem("new_key"))
        self.table.setItem(row, 1, QTableWidgetItem("value"))
        
        # Select the new row
        self.table.selectRow(row)
        self.update_value_editor()
    
    def remove_selected_row(self):
        """Remove the selected row"""
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        
        # Remove rows in reverse order to avoid index shifting
        for row in sorted(rows, reverse=True):
            self.table.removeRow(row)
        
        self.value_editor.clear()
    
    def collect_table_data(self):
        """Collect data from the table into a dictionary"""
        data = {}
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            value_item = self.table.item(row, 1)
            
            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                
                if key:  # Only add if key is not empty
                    data[key] = value
        
        return data
    
    def save_json(self):
        """Save the JSON data to the file"""
        try:
            # Collect data from the table
            data = self.collect_table_data()
            
            # If we had a parent key, restore the structure
            if self.parent_key:
                output_data = {self.parent_key: data}
            else:
                output_data = data
            
            # If no file path yet, ask for one
            if not self.file_path:
                self.file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save JSON File", "", "JSON Files (*.json)"
                )
                if not self.file_path:
                    return  # User cancelled
            
            # Write to file with pretty formatting
            with open(self.file_path, 'w') as f:
                json.dump(output_data, f, indent=4)
            
            # Sync to project directory if checkbox is checked and we have a project reference
            if self.sync_checkbox.isChecked() and self.project:
                filename = os.path.basename(self.file_path)
                
                # Check if this is a database file by checking the path
                is_db_file = PROJECTS_DB_DIR in self.file_path
                
                if is_db_file:
                    # Sync from database to project
                    project_file_path = os.path.join(self.project.path, filename)
                    shutil.copy2(self.file_path, project_file_path)
                    debug_print(f"Synced changes from database to project file: {project_file_path}")
                else:
                    # Sync from project to database
                    db_file_path = None
                    if filename == "project_info.json":
                        db_file_path = self.project.db_info_path
                    elif filename == "scripts.json":
                        db_file_path = self.project.db_scripts_path
                    
                    if db_file_path:
                        # Make sure the database directory exists
                        os.makedirs(os.path.dirname(db_file_path), exist_ok=True)
                        shutil.copy2(self.file_path, db_file_path)
                        debug_print(f"Synced changes from project to database file: {db_file_path}")
            
            QMessageBox.information(self, "Success", "JSON file saved successfully.")
            self.accept()  # Close dialog with success
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save JSON file: {str(e)}")
    
    @staticmethod
    def edit_json_file(parent, file_path, project=None):
        """Static method to create and show the dialog"""
        dialog = JsonEditorDialog(parent, file_path, project)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted 