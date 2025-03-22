from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTextEdit, QProgressBar, QMessageBox, QMenu
)
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
import os
import subprocess
import shutil
from utils.debug import debug_print
from config import SUBPROCESS_TIMEOUT, ALLOWED_SCRIPT_DIRS
from services.git_service import GitService
from views.json_editor import JsonEditorDialog

# Define common button style
button_style = "QPushButton { background-color: white; color: black; border: 1px solid #cccccc; border-radius: 4px; padding: 4px 8px; }"

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
        
        selector_label = QLabel("Select Project:")
        selector_label.setStyleSheet("font-weight: bold;")
        selector_layout.addWidget(selector_label)
        
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
        info_header = QHBoxLayout()
        project_info_label = QLabel("Project Information:")
        project_info_label.setStyleSheet("font-weight: bold;")
        info_header.addWidget(project_info_label)
        
        # Add edit button for project info
        self.edit_info_button = QPushButton("Edit")
        self.edit_info_button.setFixedWidth(80)
        self.edit_info_button.setStyleSheet(button_style)
        self.edit_info_button.clicked.connect(lambda: self.edit_json_file(self.project_service.projects[self.project_dropdown.currentIndex()], "project_info.json"))
        self.edit_info_button.setEnabled(False)  # Initially disabled until a project is selected
        info_header.addWidget(self.edit_info_button)
        info_header.addStretch()
        layout.addLayout(info_header)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(100)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)
        
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
        output_header = QHBoxLayout()
        project_output_label = QLabel("Project Output:")
        project_output_label.setStyleSheet("font-weight: bold;")
        output_header.addWidget(project_output_label)
        
        # Add edit button for scripts
        self.edit_scripts_button = QPushButton("Edit")
        self.edit_scripts_button.setFixedWidth(80)
        self.edit_scripts_button.setStyleSheet(button_style)
        self.edit_scripts_button.clicked.connect(lambda: self.edit_json_file(self.project_service.projects[self.project_dropdown.currentIndex()], "scripts.json"))
        self.edit_scripts_button.setEnabled(False)  # Initially disabled until a project is selected
        output_header.addWidget(self.edit_scripts_button)
        output_header.addStretch()
        layout.addLayout(output_header)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #f0f0f0;")
        self.output_text.setMaximumHeight(150)
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
        
        # Enable/disable edit buttons based on whether a valid project is selected
        has_valid_project = current_index >= 0 and current_index < len(self.project_service.projects)
        self.edit_info_button.setEnabled(has_valid_project)
        self.edit_scripts_button.setEnabled(has_valid_project)
        
        if not has_valid_project:
            debug_print("Invalid project index")
            return
        
        project = self.project_service.projects[current_index]
        debug_print(f"Selected project: {project.name} at {project.path}")
        
        if not project.info:
            debug_print(f"Loading project info for {project.name}")
            project.load_info()
        
        # Format project info for display with bold keys and newlines between pairs
        info_display = f"<b>Project:</b> {project.name}<br>"
        info_display += f"<b>Path:</b> {project.path}<br><br>"
        
        # Display all fields from project_info.json instead of just hardcoded ones
        # First, show common fields in a specific order if they exist
        common_fields = ['description', 'usage', 'notes']
        for field in common_fields:
            if field in project.info:
                info_display += f"<b>{field.capitalize()}:</b> {project.info.get(field, 'N/A')}<br>"
        
        # Then display any additional fields from the JSON
        for key, value in project.info.items():
            if key not in common_fields:  # Skip fields we've already displayed
                # Capitalize the key and format it nicely
                display_key = key.replace('_', ' ').capitalize()
                info_display += f"<b>{display_key}:</b> {value}<br>"
        
        # Git information removed - now shown only in Git panel
        
        self.info_text.setHtml(info_display)
        
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
        self.output_text.setHtml("<b>Scan Status:</b> Preparing to scan for projects...<br>")
        
        # Use a timer to start the scan after UI updates
        QTimer.singleShot(100, self.perform_scan)
    
    def perform_scan(self):
        """Perform the actual scan operation"""
        # Define callback for UI updates
        def update_ui(message):
            formatted_message = f"<b>Scan:</b> {message}<br>"
            self.output_text.append(formatted_message)
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
        self.output_text.append("<br><b>Scan Status:</b> <span style='color:green'>Completed</span>")
    
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
            self.output_text.append(f"<span style='color:red'>ERROR: {reason}</span>")
            return
        
        # Store the command for later execution
        self.current_command = command
        self.script_to_execute = script_name
        
        # Clear output and show command
        self.output_text.clear()
        self.output_text.setHtml(f"<b>Script:</b> {script_name}<br>")
        self.output_text.append(f"<b>Command to execute:</b> {command}<br>")
        self.output_text.append(f"<b>Working directory:</b> {project.path}<br><br>")
        self.output_text.append("<i>Click 'Execute Command' to run this command, or 'Cancel' to abort.</i>")
        
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
        
        # Disable edit buttons during command execution
        self.edit_info_button.setEnabled(False)
        self.edit_scripts_button.setEnabled(False)
        
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
        
        # Enable edit buttons
        self.edit_info_button.setEnabled(True)
        self.edit_scripts_button.setEnabled(True)
        
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
        self.output_text.clear()
        self.output_text.append("<b>Executing command:</b><br>")
        self.output_text.append(f"{command}<br>")
        self.output_text.append(f"<b>Working directory:</b> {project.path}<br><br>")
        
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
            
            # Format output as HTML with bold keys for JSON-like content
            formatted_output = self.format_output_as_html(output)
            self.output_text.append(formatted_output)
        except subprocess.TimeoutExpired:
            self.output_text.append("<span style='color:red'>ERROR: Command execution timed out.</span>")
        except Exception as e:
            self.output_text.append(f"<span style='color:red'>ERROR: {str(e)}</span>")
        finally:
            # Reset UI after execution
            self.cancel_command()

    def format_output_as_html(self, output):
        """Format command output as HTML with bold keys for JSON-like content"""
        import re
        
        # Replace < and > with their HTML entities to prevent rendering as HTML
        output = output.replace('<', '&lt;').replace('>', '&gt;')
        
        # Add formatting for JSON-like key-value pairs (key: value)
        # This regex looks for patterns like "key: value" or "key : value"
        formatted = re.sub(r'([A-Za-z0-9_-]+)\s*:\s*([^\n]+)', r'<b>\1:</b> \2<br>', output)
        
        # Also look for other common formats like key=value
        formatted = re.sub(r'([A-Za-z0-9_-]+)=([^\s]+)', r'<b>\1=</b>\2<br>', formatted)
        
        return formatted 

    def edit_json_file(self, project, file_name):
        """Open the JSON editor for a specific file"""
        # Check if a project is selected
        if not project:
            QMessageBox.critical(self, "Error", "Please select a project first.")
            return
        
        # Check for differences between project and database versions
        has_diff, db_newer, project_only, db_only, message = self.project_service.get_json_file_differences(project, file_name)
        
        if has_diff:
            # Get paths for both files
            project_file_path = os.path.join(project.path, file_name)
            db_file_path = project.get_json_file_path(file_name, prefer_db=True)
            
            # Load both files to show differences
            project_content = "{}"
            db_content = "{}"
            
            if os.path.exists(project_file_path):
                try:
                    with open(project_file_path, 'r') as f:
                        project_content = f.read()
                except Exception as e:
                    debug_print(f"Error reading project file: {str(e)}")
            
            if os.path.exists(db_file_path) and not project_only:
                try:
                    with open(db_file_path, 'r') as f:
                        db_content = f.read()
                except Exception as e:
                    debug_print(f"Error reading database file: {str(e)}")
            
            # Create a custom message box with clear button labels
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("JSON File Differences")
            
            # Create a message showing the difference
            diff_message = f"Differences found between project and database versions of {file_name}:\n\n"
            diff_message += f"{message}\n\n"
            diff_message += "Project version:\n"
            diff_message += project_content[:500] + ("..." if len(project_content) > 500 else "") + "\n\n"
            diff_message += "Database version:\n"
            diff_message += db_content[:500] + ("..." if len(db_content) > 500 else "") + "\n\n"
            diff_message += "Which version would you like to edit?"
            
            msgBox.setText(diff_message)
            msgBox.setTextFormat(Qt.TextFormat.PlainText)  # Use plain text to properly display JSON content
            
            # Add custom buttons with clear labels
            projectButton = msgBox.addButton("Use Project Version", QMessageBox.ButtonRole.YesRole)
            dbButton = msgBox.addButton("Use Database Version", QMessageBox.ButtonRole.NoRole)
            cancelButton = msgBox.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            
            # Set the default button (most logical choice based on which is newer)
            if project_only or not db_newer:
                msgBox.setDefaultButton(projectButton)
            else:
                msgBox.setDefaultButton(dbButton)
            
            # Show the dialog and get the result
            msgBox.exec()
            
            # Check which button was clicked
            clickedButton = msgBox.clickedButton()
            
            if clickedButton == cancelButton:
                return
            
            # Determine which version to use
            prefer_db = (clickedButton == dbButton)
            
            # If project only exists but user selected database, or database only exists but user selected project,
            # we need to copy the file first
            if project_only and prefer_db:
                # User wants to use database, but only project exists
                # Create database copy
                os.makedirs(os.path.dirname(db_file_path), exist_ok=True)
                shutil.copy2(project_file_path, db_file_path)
                debug_print(f"Copied project file to database: {db_file_path}")
            elif db_only and not prefer_db:
                # User wants to use project, but only database exists
                # Create project copy
                shutil.copy2(db_file_path, project_file_path)
                debug_print(f"Copied database file to project: {project_file_path}")
        else:
            # No differences found, use default preference (database)
            prefer_db = True
        
        # Get the appropriate file path based on user choice or default
        file_path = project.get_json_file_path(file_name, prefer_db=prefer_db)
        
        if not os.path.exists(file_path):
            # Check if it exists in the project directory
            project_file_path = os.path.join(project.path, file_name)
            if os.path.exists(project_file_path):
                file_path = project_file_path
            else:
                # As a fallback, check the root directory (for testing)
                root_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_name)
                if os.path.exists(root_file_path):
                    file_path = root_file_path
                else:
                    QMessageBox.critical(self, "Error", f"File {file_name} not found in project or database directory.")
                    return
        
        # Edit the file, passing the project for syncing
        if JsonEditorDialog.edit_json_file(self, file_path, project):
            # If editing was successful, refresh project info if needed
            if file_name == "project_info.json":
                project.load_info()
                self.show_project_info()
            elif file_name == "scripts.json":
                project.load_scripts()
                # Display a message to confirm changes
                self.output_text.clear()
                self.output_text.setHtml("<b>JSON Update:</b> Scripts file updated successfully.<br>")
                self.output_text.append("<b>Scripts Available:</b><br>")
                for script_name in project.scripts.keys():
                    self.output_text.append(f"• {script_name}<br>")