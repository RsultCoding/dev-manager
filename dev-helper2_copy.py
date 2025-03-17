#!/usr/bin/env python3
"""
Dev-Support Application

A PyQt6-based application for managing development projects and Docker containers.
This tool helps developers manage their projects, execute scripts, and monitor Docker.

Features:
- Project scanning and management
- Project information display
- Script execution for projects
- Docker container monitoring
- Docker image listing with a table view

Future Enhancement Ideas:
- Git integration: Pull, push, and view branch status for projects
- Environment management: Switch between dev/staging/prod environments
- Database tools: Connect to and query project databases
- Log viewer: Tail and search application logs
- Performance monitoring: Track CPU/memory usage of running containers
- Dependency analysis: Visualize and manage project dependencies
- Batch operations: Run commands across multiple projects
- Custom script editor: Create and modify project scripts within the UI
- Project templates: Create new projects from templates
- Notifications: Alert on container crashes or resource issues
- Search functionality: Find text across project files
- Dark mode support: Toggle between light and dark UI themes

Authors:
- Mikko Paalasmaa
- Claude (AI Assistant)
"""

import sys
import os
import json
import subprocess
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QTextEdit, QFrame, QMessageBox,
    QProgressBar, QSplitter, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory where this script is located
SITES_DIR = os.path.dirname(BASE_DIR)                  # Parent directory of the script directory
CACHE_FILE = os.path.join(BASE_DIR, 'projects_cache.json')  # Path to the cache file

# Debug function for logging
def debug_print(message):
    """Print debug messages with a timestamp prefix"""
    print(f"[DEBUG] {message}")

class DevSupportApp(QMainWindow):
    """
    Main application class for the Dev-Support tool.
    
    This class handles the UI creation, project management, and Docker operations.
    """
    
    def __init__(self):
        """Initialize the application window and load projects"""
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Dev-Support")
        self.setGeometry(100, 100, 1150, 600)  # Wider window for side-by-side layout
        
        debug_print(f"Base directory: {BASE_DIR}")
        debug_print(f"Sites directory: {SITES_DIR}")
        
        # Initialize project data
        self.projects = []        # List of project paths
        self.project_names = []   # List of project names (basenames)
        
        # Scan state tracking
        self.is_scanning = False  # Flag to prevent multiple scans
        self.scan_timer = None    # Timer for delayed scanning
        
        # Load projects from cache file
        self.load_cached_projects()
        
        # Create the user interface
        self.create_ui()
    
    def create_ui(self):
        """
        Create the user interface with a side-by-side layout:
        - Left side: Project management
        - Right side: Docker management
        """
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Create a splitter for the two main sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent sections from collapsing
        
        # =====================================================================
        # Left side - Project section (550px)
        # =====================================================================
        project_widget = QWidget()
        project_widget.setMinimumWidth(550)
        project_layout = QVBoxLayout(project_widget)
        
        # Project section title
        project_title = QLabel("Project Management")
        project_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        project_layout.addWidget(project_title)
        
        # Top frame with project selector and scan button
        top_frame = QWidget()
        top_layout = QHBoxLayout(top_frame)
        
        project_label = QLabel("Select Project:")
        top_layout.addWidget(project_label)
        
        # Project dropdown for selecting projects
        self.project_dropdown = QComboBox()
        self.project_dropdown.addItems(self.project_names)
        self.project_dropdown.currentIndexChanged.connect(self.show_project_info)
        self.project_dropdown.setMinimumWidth(300)  # Make dropdown wider for long project names
        top_layout.addWidget(self.project_dropdown)
        
        # Scan button to find projects
        self.scan_button = QPushButton("Scan Now")
        self.scan_button.clicked.connect(self.start_scan)
        top_layout.addWidget(self.scan_button)
        
        top_layout.addStretch()
        project_layout.addWidget(top_frame)
        
        # Progress bar for scan operation (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        project_layout.addWidget(self.progress_bar)
        
        # Project info section - displays details about the selected project
        project_layout.addWidget(QLabel("Project Information:"))
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(100)
        project_layout.addWidget(self.info_text)
        
        # Command buttons for project operations
        btn_frame = QWidget()
        btn_layout = QHBoxLayout(btn_frame)
        
        # Button to execute the 'Start Dev' script
        start_dev_button = QPushButton("Execute 'Start Dev'")
        start_dev_button.clicked.connect(lambda: self.run_script('Start Dev'))
        btn_layout.addWidget(start_dev_button)
        
        # Button to execute the 'Run Tests' script
        run_tests_button = QPushButton("Execute 'Run Tests'")
        run_tests_button.clicked.connect(lambda: self.run_script('Run Tests'))
        btn_layout.addWidget(run_tests_button)
        
        btn_layout.addStretch()
        project_layout.addWidget(btn_frame)
        
        # Project output section - displays results of operations
        project_layout.addWidget(QLabel("Project Output:"))
        self.project_output_text = QTextEdit()
        self.project_output_text.setReadOnly(True)
        self.project_output_text.setStyleSheet("background-color: #f0f0f0;")
        project_layout.addWidget(self.project_output_text)
        
        # =====================================================================
        # Right side - Docker section (600px)
        # =====================================================================
        docker_widget = QWidget()
        docker_widget.setMinimumWidth(600)  # Wider to accommodate the table
        docker_layout = QVBoxLayout(docker_widget)
        
        # Docker section title
        docker_title = QLabel("Docker Management")
        docker_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        docker_layout.addWidget(docker_title)
        
        # Docker buttons
        docker_btn_frame = QWidget()
        docker_btn_layout = QHBoxLayout(docker_btn_frame)
        
        # Button to check Docker containers
        docker_button = QPushButton("Check Docker Containers")
        docker_button.clicked.connect(self.check_docker)
        docker_btn_layout.addWidget(docker_button)
        
        # Button to list Docker images
        docker_images_button = QPushButton("List Docker Images")
        docker_images_button.clicked.connect(self.list_docker_images)
        docker_btn_layout.addWidget(docker_images_button)
        
        docker_btn_layout.addStretch()
        docker_layout.addWidget(docker_btn_frame)
        
        # Docker output section label
        docker_layout.addWidget(QLabel("Docker Output:"))
        
        # Text area for Docker container output
        self.docker_output_text = QTextEdit()
        self.docker_output_text.setReadOnly(True)
        self.docker_output_text.setStyleSheet("background-color: #f0f0f0;")
        
        # Table for Docker images (hidden by default)
        self.docker_images_table = QTableWidget()
        self.docker_images_table.setColumnCount(5)
        self.docker_images_table.setHorizontalHeaderLabels(["REPOSITORY", "TAG", "IMAGE ID", "CREATED", "SIZE"])
        
        # Configure column sizing behavior
        self.docker_images_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Repository column stretches
        self.docker_images_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Other columns resize to content
        self.docker_images_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.docker_images_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.docker_images_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.docker_images_table.setVisible(False)  # Hidden initially
        
        # Add both output widgets to the Docker section
        docker_layout.addWidget(self.docker_output_text)
        docker_layout.addWidget(self.docker_images_table)
        
        # =====================================================================
        # Finalize layout
        # =====================================================================
        
        # Add widgets to splitter
        splitter.addWidget(project_widget)
        splitter.addWidget(docker_widget)
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Select first project if available
        if self.project_names:
            self.project_dropdown.setCurrentIndex(0)
            self.show_project_info()
    
    def load_cached_projects(self):
        """
        Load projects from the cache file.
        
        This method reads the projects_cache.json file and populates
        the projects and project_names lists. It also filters out
        any projects that no longer exist on the filesystem.
        """
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache_data = json.load(f)
                    self.projects = cache_data.get('projects', [])
                    
                    # Filter out any projects that no longer exist
                    existing_projects = []
                    for p in self.projects:
                        if os.path.exists(p):
                            existing_projects.append(p)
                        else:
                            debug_print(f"Skipping non-existent project: {p}")
                    
                    # Update projects list with only existing projects
                    self.projects = existing_projects
                    # Extract project names (basenames) from paths
                    self.project_names = [os.path.basename(p) for p in self.projects]
                    debug_print(f"Loaded {len(self.projects)} projects from cache")
            except Exception as e:
                debug_print(f"Error loading cache: {str(e)}")
                self.projects = []
                self.project_names = []
        else:
            debug_print("No cache file found")
            self.projects = []
            self.project_names = []
    
    def save_cache(self):
        """
        Save projects to the cache file.
        
        This method saves the current list of projects to the
        projects_cache.json file with a timestamp.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure projects exist before saving
            existing_projects = [p for p in self.projects if os.path.exists(p)]
            
            # Prepare cache data with timestamp
            cache_data = {
                'timestamp': time.time(),
                'projects': existing_projects
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            
            # Write to cache file
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            debug_print(f"Saved {len(existing_projects)} projects to cache")
            return True
        except Exception as e:
            debug_print(f"Error saving cache: {str(e)}")
            self.project_output_text.append(f"Error saving cache: {str(e)}")
            return False
    
    def start_scan(self):
        """
        Start the scan process with immediate UI feedback.
        
        This method provides immediate visual feedback when the scan
        button is clicked, then uses a timer to start the actual scan
        after a short delay to ensure the UI updates are visible.
        """
        # Prevent multiple scans
        if self.is_scanning:
            return
            
        # Update UI to show scanning state
        self.is_scanning = True
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        
        # Clear output and show initial message
        self.project_output_text.clear()
        self.project_output_text.append("Preparing to scan for projects...")
        self.project_output_text.append(f"Looking in: {SITES_DIR}\n")
        QApplication.processEvents()  # Force UI update
        
        # Use a timer to start the actual scan after a short delay
        # This ensures the UI updates are visible immediately
        QTimer.singleShot(100, self.scan_projects)
    
    def scan_projects(self):
        """
        Scan for projects and update the UI.
        
        This method walks through the SITES_DIR directory looking for
        project_info.json files, which indicate a project directory.
        It updates the UI as projects are found and saves the results
        to the cache file.
        """
        # Find projects
        found_projects = []
        project_count = 0
        
        try:
            debug_print(f"Starting scan in {SITES_DIR}")
            self.project_output_text.append("Scanning started...")
            QApplication.processEvents()  # Force UI update
            
            # Walk through the directory tree
            for root, dirs, files in os.walk(SITES_DIR):
                # Skip hidden directories (those starting with a dot)
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Check if this directory contains a project_info.json file
                if 'project_info.json' in files:
                    project_count += 1
                    found_projects.append(root)
                    project_name = os.path.basename(root)
                    debug_print(f"Found project: {root}")
                    
                    # Update UI for each project found
                    self.project_output_text.append(f"Found project: {project_name}")
                    QApplication.processEvents()  # Force UI update
            
            # Update the projects list with found projects
            self.projects = found_projects
            
            # Update project names
            self.project_names = [os.path.basename(p) for p in self.projects]
            debug_print(f"Project names after scan: {self.project_names}")
            
            # Save to cache
            if self.save_cache():
                debug_print("Cache updated successfully")
                self.project_output_text.append("Cache updated successfully.")
            else:
                debug_print("Failed to update cache")
                self.project_output_text.append("Failed to update cache.")
            
            # Update dropdown values
            self.project_dropdown.clear()
            self.project_dropdown.addItems(self.project_names)
            
            # Show result
            self.project_output_text.append(f"\nScan complete. Found {len(self.projects)} projects.\n")
            for project in self.project_names:
                self.project_output_text.append(f"- {project}")
            
            # Select first project if available
            if self.project_names:
                self.project_dropdown.setCurrentIndex(0)
                debug_print(f"Selected first project: {self.project_names[0]}")
            else:
                debug_print("No projects found to select")
                
        except Exception as e:
            debug_print(f"Error during scan: {str(e)}")
            self.project_output_text.append(f"Error during scan: {str(e)}")
        finally:
            # Reset UI state regardless of success or failure
            self.is_scanning = False
            self.scan_button.setEnabled(True)
            self.scan_button.setText("Scan Now")
            self.progress_bar.setVisible(False)
            QApplication.processEvents()  # Force UI update
    
    def show_project_info(self):
        """
        Show information about the selected project.
        
        This method reads the project_info.json file for the selected
        project and displays its contents in the info text area.
        """
        # Check if there are any projects
        if not self.project_names:
            debug_print("No projects available")
            return
            
        # Get the selected project index
        current_index = self.project_dropdown.currentIndex()
        if current_index < 0:
            debug_print("No project selected")
            return
            
        # Get the project name and path
        project_name = self.project_names[current_index]
        debug_print(f"Showing info for project: {project_name}")
        project_path = next((p for p in self.projects if os.path.basename(p) == project_name), None)
        
        if not project_path:
            debug_print(f"Project path not found for: {project_name}")
            return
        
        # Read and display the project info
        info_file = os.path.join(project_path, 'project_info.json')
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    
                # Format the project info for display
                self.info_text.clear()
                info_display = f"Project: {project_name}\n"
                info_display += f"Path: {project_path}\n\n"
                info_display += f"Description: {info.get('description','N/A')}\n"
                info_display += f"Usage: {info.get('usage','N/A')}\n"
                info_display += f"Notes: {info.get('notes','')}"
                self.info_text.setPlainText(info_display)
                debug_print("Project info displayed")
            except Exception as e:
                debug_print(f"Error loading project info: {str(e)}")
                self.info_text.setPlainText(f"Error loading project info: {str(e)}")
        else:
            debug_print(f"Project info file not found: {info_file}")
            self.info_text.setPlainText("Project info file not found.")
    
    def run_script(self, script_name):
        """
        Run a script from the selected project.
        
        This method reads the scripts.json file for the selected project,
        finds the specified script, and executes it in the project directory.
        
        Args:
            script_name (str): The name of the script to run (e.g., 'Start Dev')
        """
        # Check if there are any projects
        if not self.project_names:
            QMessageBox.critical(self, "Error", "No projects available.")
            return
            
        # Get the selected project index
        current_index = self.project_dropdown.currentIndex()
        if current_index < 0:
            QMessageBox.critical(self, "Error", "Please select a project first.")
            return
            
        # Get the project name and path
        project_name = self.project_names[current_index]
        debug_print(f"Running script '{script_name}' for project '{project_name}'")
        project_path = next((p for p in self.projects if os.path.basename(p) == project_name), None)
        
        if not project_path:
            debug_print(f"Project path not found for: {project_name}")
            QMessageBox.critical(self, "Error", "Project path not found.")
            return
        
        # Read the scripts file
        scripts_file = os.path.join(project_path, 'scripts.json')
        debug_print(f"Looking for scripts file at: {scripts_file}")
        
        if os.path.exists(scripts_file):
            try:
                # Load the scripts from the file
                with open(scripts_file, 'r') as f:
                    scripts_data = json.load(f)
                    scripts = scripts_data.get('scripts', {})
                    debug_print(f"Available scripts: {list(scripts.keys())}")
                
                # Get the command for the specified script
                command = scripts.get(script_name)
                if command:
                    debug_print(f"Found command: {command}")
                    self.project_output_text.clear()
                    self.project_output_text.append(f"Running: {command}")
                    self.project_output_text.append(f"Working directory: {project_path}\n")
                    QApplication.processEvents()  # Force UI update
                    
                    try:
                        # Execute the command in the project directory
                        debug_print(f"Executing command: {command} in {project_path}")
                        result = subprocess.run(command, shell=True, cwd=project_path, 
                                              capture_output=True, text=True)
                        output = result.stdout + result.stderr
                        debug_print(f"Command output: {output}")
                        self.project_output_text.append(output)
                    except Exception as e:
                        debug_print(f"Error executing command: {str(e)}")
                        self.project_output_text.append(str(e))
                else:
                    debug_print(f"Script '{script_name}' not found in available scripts")
                    QMessageBox.critical(self, "Error", f"Script '{script_name}' not defined.")
            except Exception as e:
                debug_print(f"Error loading scripts file: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error loading scripts: {str(e)}")
        else:
            debug_print(f"Scripts file not found: {scripts_file}")
            QMessageBox.critical(self, "Error", "scripts.json not found.")
    
    def check_docker(self):
        """
        Check Docker containers.
        
        This method executes the 'docker ps' command to list running
        containers and displays the output in the Docker output text area.
        """
        # Clear output and show Docker containers text view
        self.docker_output_text.clear()
        self.docker_output_text.setVisible(True)
        self.docker_images_table.setVisible(False)
        self.docker_output_text.append("Checking Docker containers...\n")
        QApplication.processEvents()  # Force UI update
        
        try:
            # Execute the docker ps command
            debug_print("Executing 'docker ps' command")
            result = subprocess.run('docker ps', shell=True, cwd=BASE_DIR, 
                                  capture_output=True, text=True)
            output = result.stdout + result.stderr
            debug_print(f"Docker command output: {output}")
            self.docker_output_text.append(output)
        except Exception as e:
            debug_print(f"Error checking Docker: {str(e)}")
            self.docker_output_text.append(str(e))
    
    def list_docker_images(self):
        """
        List Docker images in a table.
        
        This method executes the 'docker images' command and displays
        the results in a table format for better readability.
        """
        # Clear output and show Docker images table
        self.docker_output_text.clear()
        self.docker_output_text.setVisible(False)
        self.docker_images_table.setVisible(True)
        self.docker_images_table.setRowCount(0)  # Clear existing rows
        QApplication.processEvents()  # Force UI update
        
        try:
            # Execute the docker images command
            debug_print("Executing 'docker images' command")
            result = subprocess.run('docker images', shell=True, cwd=BASE_DIR, 
                                  capture_output=True, text=True)
            output = result.stdout + result.stderr
            debug_print(f"Docker images command output: {output}")
            
            # Check if there's an error message
            if "Cannot connect to the Docker daemon" in output or "Is the docker daemon running" in output:
                # Show error in text view instead of table
                self.docker_output_text.setVisible(True)
                self.docker_images_table.setVisible(False)
                self.docker_output_text.append(output)
                return
                
            # Parse the output and populate the table
            lines = output.strip().split('\n')
            if len(lines) > 1:  # Header + at least one row
                # Skip the header row (first line)
                for i, line in enumerate(lines[1:]):
                    columns = line.split()
                    if len(columns) >= 5:
                        # Handle multi-word repository names
                        if len(columns) > 5:
                            # Combine all elements except the last 4 into the repository name
                            repo = " ".join(columns[:-4])
                            tag = columns[-4]
                            image_id = columns[-3]
                            created = " ".join(columns[-2:-1])
                            size = columns[-1]
                        else:
                            # Standard format with 5 columns
                            repo = columns[0]
                            tag = columns[1]
                            image_id = columns[2]
                            created = " ".join(columns[3:-1])
                            size = columns[-1]
                        
                        # Add a new row to the table
                        row_position = self.docker_images_table.rowCount()
                        self.docker_images_table.insertRow(row_position)
                        
                        # Add items to the row
                        self.docker_images_table.setItem(row_position, 0, QTableWidgetItem(repo))
                        self.docker_images_table.setItem(row_position, 1, QTableWidgetItem(tag))
                        self.docker_images_table.setItem(row_position, 2, QTableWidgetItem(image_id))
                        self.docker_images_table.setItem(row_position, 3, QTableWidgetItem(created))
                        self.docker_images_table.setItem(row_position, 4, QTableWidgetItem(size))
            else:
                # No images or error
                self.docker_output_text.setVisible(True)
                self.docker_images_table.setVisible(False)
                self.docker_output_text.append("No Docker images found or error occurred.")
                
        except Exception as e:
            debug_print(f"Error listing Docker images: {str(e)}")
            self.docker_output_text.setVisible(True)
            self.docker_images_table.setVisible(False)
            self.docker_output_text.append(str(e))

def main():
    """
    Main entry point for the application.
    
    Creates the QApplication, shows the main window, and starts the event loop.
    """
    app = QApplication(sys.argv)
    window = DevSupportApp()
    window.show()
    
    debug_print("Starting application")
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 