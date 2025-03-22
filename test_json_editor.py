#!/usr/bin/env python3
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
import sys
import os
from views.json_editor import JsonEditorDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Editor Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout(central)
        
        # Open file button
        self.open_btn = QPushButton("Open JSON File...")
        self.open_btn.clicked.connect(self.open_file)
        layout.addWidget(self.open_btn)
        
        # Test with scripts.json button
        self.scripts_btn = QPushButton("Edit scripts.json")
        self.scripts_btn.clicked.connect(self.edit_scripts)
        layout.addWidget(self.scripts_btn)
        
        # Test with project_info.json button
        self.info_btn = QPushButton("Edit project_info.json")
        self.info_btn.clicked.connect(self.edit_project_info)
        layout.addWidget(self.info_btn)
    
    def open_file(self):
        """Open a JSON file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json)"
        )
        
        if file_path:
            JsonEditorDialog.edit_json_file(self, file_path)
    
    def edit_scripts(self):
        """Edit the scripts.json file"""
        scripts_path = os.path.join(os.path.dirname(__file__), "scripts.json")
        if os.path.exists(scripts_path):
            JsonEditorDialog.edit_json_file(self, scripts_path)
        else:
            print(f"scripts.json not found at {scripts_path}")
    
    def edit_project_info(self):
        """Edit the project_info.json file"""
        info_path = os.path.join(os.path.dirname(__file__), "project_info.json")
        if os.path.exists(info_path):
            JsonEditorDialog.edit_json_file(self, info_path)
        else:
            print(f"project_info.json not found at {info_path}")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 