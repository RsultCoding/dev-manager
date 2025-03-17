from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTextEdit, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
import os
import subprocess
from utils.debug import debug_print
from config import SUBPROCESS_TIMEOUT, ALLOWED_SCRIPT_DIRS
from views.git_panel import GitPanel

class ProjectPanel(QWidget):
    def __init__(self, project_service):
        super().__init__()
        self.project_service = project_service
        self.current_command = None
        self.script_to_execute = None
        self.create_ui()
    
    def create_ui(self):
        """Create the project panel UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("Project Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Project selector section
        selector_frame = QWidget()
        selector_layout = QHBoxLayout(selector_frame)
        
        selector_layout.addWidget(QLabel("Select Project:"))
        
        # Project dropdown
        self.project_dropdown = QComboBox()
        # Print the styleSheet of the project dropdown for debugging
        debug_print(f"Project dropdown styleSheet: {self.project_dropdown.styleSheet()}")
        self.project_dropdown.setMinimumWidth(300)
        selector_layout.addWidget(self.project_dropdown)
        
        # Scan button
        self.scan_button = QPushButton("Scan Now")
        self.scan_button.clicked.connect(self.start_scan)
        selector_layout.addWidget(self.scan_button)
        
        selector_layout.addStretch()
        layout.addWidget(selector_frame)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Project info section
        layout.addWidget(QLabel("Project Information:"))
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(100)
        layout.addWidget(self.info_text)
        
        # Git panel section - must be created before calling update_project_dropdown
        git_label = QLabel("Git Operations:")
        git_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(git_label)
        
        self.git_panel = GitPanel(self.project_service)
        self.git_panel.setVisible(True)  # Ensure the panel is visible
        layout.addWidget(self.git_panel)
        
        # Command buttons
        btn_frame = QWidget()
        btn_layout = QHBoxLayout(btn_frame)
        
        # Create button frame for script buttons
        script_btn_frame = QWidget()
        script_btn_layout = QHBoxLayout(script_btn_frame)
        script_btn_layout.setContentsMargins(0, 0, 0, 0)
        script_btn_layout.setSpacing(5)  # Reduce spacing between buttons
        
        # Script execution buttons
        self.start_dev_button = QPushButton("'Start Dev'")
        self.start_dev_button.clicked.connect(lambda: self.show_script_command('Start Dev'))
        self.start_dev_button.setFixedWidth(100)
        script_btn_layout.addWidget(self.start_dev_button)
        
        self.run_tests_button = QPushButton("'Run Tests'")
        self.run_tests_button.clicked.connect(lambda: self.show_script_command('Run Tests'))
        self.run_tests_button.setFixedWidth(100)
        script_btn_layout.addWidget(self.run_tests_button)
        
        # Add three placeholder buttons
        self.placeholder1_button = QPushButton("'Placeholder 1'")
        self.placeholder1_button.clicked.connect(lambda: self.show_script_command('Placeholder 1'))
        self.placeholder1_button.setFixedWidth(100)
        script_btn_layout.addWidget(self.placeholder1_button)
        
        self.placeholder2_button = QPushButton("'Placeholder 2'")
        self.placeholder2_button.clicked.connect(lambda: self.show_script_command('Placeholder 2'))
        self.placeholder2_button.setFixedWidth(100)
        script_btn_layout.addWidget(self.placeholder2_button)
        
        self.placeholder3_button = QPushButton("'Placeholder 3'")
        self.placeholder3_button.clicked.connect(lambda: self.show_script_command('Placeholder 3'))
        self.placeholder3_button.setFixedWidth(100)
        script_btn_layout.addWidget(self.placeholder3_button)
        
        # Add the script button frame to the main button layout
        btn_layout.addWidget(script_btn_frame)
        
        # Execute button (hidden by default)
        self.execute_button = QPushButton("Execute Command")
        self.execute_button.clicked.connect(self.execute_command)
        self.execute_button.setVisible(False)
        self.execute_button.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_layout.addWidget(self.execute_button)
        
        # Cancel button (hidden by default)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_command)
        self.cancel_button.setVisible(False)
        btn_layout.addWidget(self.cancel_button)
        
        btn_layout.addStretch()
        layout.addWidget(btn_frame)
        
        # Project output section
        layout.addWidget(QLabel("Project Output:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #f0f0f0;")
        layout.addWidget(self.output_text)

        # NOW that all UI elements are created, connect the signal and update the dropdown
        self.project_dropdown.currentIndexChanged.connect(self.show_project_info)
        self.update_project_dropdown()
        
        debug_print("UI creation complete")
    
    def update_project_dropdown(self):
        """Update the project dropdown with current projects"""
        self.project_dropdown.clear()
        project_names = [project.name for project in self.project_service.projects]
        self.project_dropdown.addItems(project_names)
        
        # Try to select the current project (dev-manager) by default
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.path.dirname(current_dir)  # Go up one level to get the project root
        debug_print(f"Current directory for project selection: {current_dir}")
        
        # Find the current project in the list
        current_project_index = -1
        for i, project in enumerate(self.project_service.projects):
            if project.path == current_dir:
                current_project_index = i
                debug_print(f"Found current project at index {i}: {project.name}")
                break
        
        # Select the current project if found, otherwise select the first project
        if current_project_index >= 0:
            self.project_dropdown.setCurrentIndex(current_project_index)
        elif self.project_dropdown.count() > 0:
            self.project_dropdown.setCurrentIndex(0)
        
        # Don't call show_project_info here - it will be triggered by the signal
    
    def show_project_info(self):
        """Display information about the selected project"""
        current_index = self.project_dropdown.currentIndex()
        debug_print(f"show_project_info called with index: {current_index}")
        
        if current_index < 0 or current_index >= len(self.project_service.projects):
            debug_print("Invalid project index")
            return
        
        project = self.project_service.projects[current_index]
        debug_print(f"Selected project: {project.name} at {project.path}")
        
        if not project.info:
            debug_print(f"Loading project info for {project.name}")
            project.load_info()
        
        # Format project info for display
        info_display = f"Project: {project.name}\n"
        info_display += f"Path: {project.path}\n\n"
        info_display += f"Description: {project.info.get('description','N/A')}\n"
        info_display += f"Usage: {project.info.get('usage','N/A')}\n"
        info_display += f"Notes: {project.info.get('notes','')}"
        
        # Update Git panel for selected project first to get Git info loaded
        debug_print(f"Updating Git panel for project: {project.name}")
        self.git_panel.update_for_project(project)
        
        # Add Git repository information if available
        debug_print(f"Project is_git_repo: {project.is_git_repo}")
        if project.is_git_repo:
            modified_count = project.get_modified_files_count()
            debug_print(f"Modified files count: {modified_count}")
            info_display += f"\n\nGit Repository: Yes (Branch: {project.current_branch})"
            if modified_count > 0:
                info_display += f"\nModified Files: {modified_count}"
        
        self.info_text.setPlainText(info_display)
        
        # Reset command execution UI
        self.cancel_command()
    
    def start_scan(self):
        """Start the scan process with immediate UI feedback"""
        if self.project_service.is_scanning:
            return
        
        # Update UI
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        self.progress_bar.setVisible(True)
        
        # Clear output and show initial message
        self.output_text.clear()
        self.output_text.append("Preparing to scan for projects...")
        
        # Use a timer to start the scan after UI updates
        QTimer.singleShot(100, self.perform_scan)
    
    def perform_scan(self):
        """Perform the actual scan operation"""
        # Define callback for UI updates
        def update_ui(message):
            self.output_text.append(message)
            self.output_text.repaint()
        
        # Execute scan
        self.project_service.scan_projects(callback=update_ui)
        
        # Update UI after scan
        self.update_project_dropdown()
        
        if self.project_dropdown.count() > 0:
            self.project_dropdown.setCurrentIndex(0)
            self.show_project_info()
        
        # Reset UI state
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Scan Now")
        self.progress_bar.setVisible(False)
    
    def show_script_command(self, script_name):
        """Show the command that would be executed for a script"""
        current_index = self.project_dropdown.currentIndex()
        if current_index < 0 or current_index >= len(self.project_service.projects):
            QMessageBox.critical(self, "Error", "Please select a project first.")
            return
        
        project = self.project_service.projects[current_index]
        
        # Load scripts if not already loaded
        if not project.scripts:
            project.load_scripts()
        
        # Get the command for the specified script
        command = project.scripts.get(script_name)
        if not command:
            QMessageBox.critical(self, "Error", f"Script '{script_name}' not defined.")
            return
        
        # Security check - ensure the project path is in allowed directories
        if not any(project.path.startswith(allowed_dir) for allowed_dir in ALLOWED_SCRIPT_DIRS):
            QMessageBox.critical(self, "Security Error", "Cannot execute scripts in this location.")
            debug_print(f"Security check failed for path: {project.path}")
            return
        
        # Script validation
        is_valid, reason = self.project_service.validate_script(command)
        if not is_valid:
            QMessageBox.critical(self, "Security Error", f"Cannot execute script: {reason}")
            self.output_text.append(f"ERROR: {reason}")
            return
        
        # Store the command for later execution
        self.current_command = command
        self.script_to_execute = script_name
        
        # Clear output and show command
        self.output_text.clear()
        self.output_text.append(f"Command to execute: {command}")
        self.output_text.append(f"Working directory: {project.path}\n")
        self.output_text.append("Click 'Execute Command' to run this command, or 'Cancel' to abort.")
        
        # Update UI to show execution buttons
        self.update_ui_for_command_confirmation()
    
    def update_ui_for_command_confirmation(self):
        """Update UI to show execution confirmation buttons"""
        # Hide script buttons
        self.start_dev_button.setVisible(False)
        self.run_tests_button.setVisible(False)
        self.placeholder1_button.setVisible(False)
        self.placeholder2_button.setVisible(False)
        self.placeholder3_button.setVisible(False)
        
        # Show execution buttons
        self.execute_button.setVisible(True)
        self.cancel_button.setVisible(True)
    
    def cancel_command(self):
        """Cancel the command execution"""
        # Reset stored command
        self.current_command = None
        self.script_to_execute = None
        
        # Show script buttons
        self.start_dev_button.setVisible(True)
        self.run_tests_button.setVisible(True)
        self.placeholder1_button.setVisible(True)
        self.placeholder2_button.setVisible(True)
        self.placeholder3_button.setVisible(True)
        
        # Hide execution buttons
        self.execute_button.setVisible(False)
        self.cancel_button.setVisible(False)
    
    def execute_command(self):
        """Execute the previously shown command"""
        if not self.current_command or not self.script_to_execute:
            return
        
        current_index = self.project_dropdown.currentIndex()
        if current_index < 0 or current_index >= len(self.project_service.projects):
            return
        
        project = self.project_service.projects[current_index]
        command = self.current_command
        
        # Update output to show execution
        self.output_text.append("\nExecuting command...\n")
        
        try:
            # Execute the command with timeout
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=project.path,
                capture_output=True, 
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            output = result.stdout + result.stderr
            self.output_text.append(output)
        except subprocess.TimeoutExpired:
            self.output_text.append("ERROR: Command execution timed out.")
        except Exception as e:
            self.output_text.append(f"ERROR: {str(e)}")
        finally:
            # Reset UI after execution
            self.cancel_command() 