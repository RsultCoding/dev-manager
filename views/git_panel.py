from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QFrame, QCheckBox, QLineEdit,
    QGroupBox, QMessageBox, QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from utils.debug import debug_print
from services.git_service import GitService
import subprocess

class GitPanel(QWidget):
    def __init__(self, project_service):
        super().__init__()
        self.project_service = project_service
        self.git_service = GitService()
        self.current_project = None
        self.status_timer = None
        self.create_ui()
    
    def create_ui(self):
        """Create the Git panel UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.Box)
        scroll_area.setStyleSheet("border: 1px solid #cccccc;")
        
        # Create container widget for scroll area
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: none; border: none;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        
        # Git panel title with current branch
        header_layout = QHBoxLayout()
        title = QLabel("Git Operations")
        title.setStyleSheet("font-weight: bold; background: none; border: none;")
        header_layout.addWidget(title)
        
        self.branch_label = QLabel("Current Branch: main")
        self.branch_label.setStyleSheet("color: #0066cc; background: none; border: none;")
        header_layout.addWidget(self.branch_label, alignment=Qt.AlignmentFlag.AlignRight)
        scroll_layout.addLayout(header_layout)
        
        # Define button style before using it
        button_style = "QPushButton { background-color: white; color: black; border: 1px solid #cccccc; border-radius: 4px; padding: 4px 8px; }"
        
        # Branch selector section - recreated to match Project selector exactly
        branch_frame = QWidget()
        branch_layout = QHBoxLayout(branch_frame)
        
        # Create label exactly like "Select Project:" label
        branch_label = QLabel("Branch:")
        branch_layout.addWidget(branch_label)
        
        # Reset branch dropdown to match project dropdown exactly with explicit styling
        self.branch_dropdown = QComboBox()
        self.branch_dropdown.setMinimumWidth(300)
        # Simple styling to match project dropdown
        self.branch_dropdown.setStyleSheet("")  # Reset any styling to use platform default
        self.branch_dropdown.currentIndexChanged.connect(self.on_branch_selection_changed)
        branch_layout.addWidget(self.branch_dropdown)
        
        # Buttons in the same style as "Scan Now"
        checkout_btn = QPushButton("Checkout")
        checkout_btn.clicked.connect(self.on_checkout_branch)
        branch_layout.addWidget(checkout_btn)
        
        new_branch_btn = QPushButton("New")
        new_branch_btn.setToolTip("Create a new branch")
        new_branch_btn.clicked.connect(self.on_create_branch)
        branch_layout.addWidget(new_branch_btn)
        
        # Add stretch to push refresh button to the right
        branch_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("⟳")
        refresh_btn.setToolTip("Refresh Git status and branches")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self.refresh_git_panel)
        branch_layout.addWidget(refresh_btn)
        
        # Add the frame to the main layout
        scroll_layout.addWidget(branch_frame)
        
        # Status message area
        self.status_message = QLabel("")
        self.status_message.setStyleSheet("color: #888888; font-style: italic; padding: 4px;")
        self.status_message.setWordWrap(True)
        scroll_layout.addWidget(self.status_message)
        
        # Modified files section
        self.files_label = QLabel("Modified Files (0)")
        self.files_label.setStyleSheet("font-weight: bold; background: none; border: none;")
        scroll_layout.addWidget(self.files_label)
        
        # Container for file checkboxes
        self.files_widget = QWidget()
        self.files_widget.setStyleSheet("background: none; border: none;")
        self.files_layout = QVBoxLayout(self.files_widget)
        self.files_layout.setContentsMargins(0, 0, 0, 0)
        self.files_layout.setSpacing(3)
        
        self.file_checkboxes = {}  # Dictionary to store checkboxes by file path
        scroll_layout.addWidget(self.files_widget)
        
        # Actions section
        actions_label = QLabel("Actions")
        actions_label.setStyleSheet("font-weight: bold; background: none; border: none;")
        scroll_layout.addWidget(actions_label)
        
        actions_widget = QWidget()
        actions_widget.setStyleSheet("background: none; border: none;")
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        stage_all_btn = QPushButton("Stage All")
        stage_all_btn.setStyleSheet(button_style)
        stage_all_btn.clicked.connect(self.on_stage_all)
        actions_layout.addWidget(stage_all_btn)
        
        unstage_all_btn = QPushButton("Unstage All")
        unstage_all_btn.setStyleSheet(button_style)
        unstage_all_btn.clicked.connect(self.on_unstage_all)
        actions_layout.addWidget(unstage_all_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(button_style)
        refresh_btn.clicked.connect(self.on_refresh)
        actions_layout.addWidget(refresh_btn)
        
        scroll_layout.addWidget(actions_widget)
        
        # Commit section
        commit_label = QLabel("Commit Message:")
        commit_label.setStyleSheet("font-weight: bold; background: none; border: none;")
        scroll_layout.addWidget(commit_label)
        
        self.commit_message = QTextEdit()
        self.commit_message.setMaximumHeight(80)
        self.commit_message.setPlaceholderText("Enter commit message here...")
        self.commit_message.setStyleSheet("border: 1px solid #cccccc; border-radius: 4px;")
        scroll_layout.addWidget(self.commit_message)
        
        commit_btns = QHBoxLayout()
        
        commit_push_btn = QPushButton("Commit & Push")
        commit_push_btn.clicked.connect(self.on_commit_push)
        commit_push_btn.setStyleSheet(button_style)
        commit_btns.addWidget(commit_push_btn)
        
        commit_only_btn = QPushButton("Commit Only")
        commit_only_btn.setStyleSheet(button_style)
        commit_only_btn.clicked.connect(self.on_commit)
        commit_btns.addWidget(commit_only_btn)
        
        scroll_layout.addLayout(commit_btns)
        
        # Quick actions section
        quick_label = QLabel("Quick Actions")
        quick_label.setStyleSheet("font-weight: bold; background: none; border: none;")
        scroll_layout.addWidget(quick_label)
        
        quick_widget = QWidget()
        quick_widget.setStyleSheet("background: none; border: none;")
        quick_layout = QHBoxLayout(quick_widget)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        
        pull_btn = QPushButton("Pull")
        pull_btn.setStyleSheet(button_style)
        pull_btn.clicked.connect(self.on_pull)
        quick_layout.addWidget(pull_btn)
        
        push_btn = QPushButton("Push")
        push_btn.setStyleSheet(button_style)
        push_btn.clicked.connect(self.on_push)
        quick_layout.addWidget(push_btn)
        
        stash_btn = QPushButton("Stash")
        stash_btn.setStyleSheet(button_style)
        stash_btn.clicked.connect(self.on_stash)
        quick_layout.addWidget(stash_btn)
        
        pop_stash_btn = QPushButton("Pop Stash")
        pop_stash_btn.setStyleSheet(button_style)
        pop_stash_btn.clicked.connect(self.on_pop_stash)
        quick_layout.addWidget(pop_stash_btn)
        
        scroll_layout.addWidget(quick_widget)
        
        # Recent commits section
        recent_label = QLabel("Recent Commits:")
        recent_label.setStyleSheet("font-weight: bold; background: none; border: none;")
        scroll_layout.addWidget(recent_label)
        
        self.recent_commits = QTextEdit()
        self.recent_commits.setReadOnly(True)
        self.recent_commits.setMaximumHeight(100)
        self.recent_commits.setStyleSheet("background-color: #f9f9f9; border: none;")
        scroll_layout.addWidget(self.recent_commits)
        
        # Set the scroll widget
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Initially disable the panel
        self.setEnabled(False)
    
    def clear_file_checkboxes(self):
        """Clear all file checkboxes"""
        for checkbox in self.file_checkboxes.values():
            self.files_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.file_checkboxes = {}
    
    def update_file_checkboxes(self):
        """Update the file checkboxes based on current Git status"""
        if not self.current_project or not self.current_project.git_status:
            return
        
        # Clear existing checkboxes
        self.clear_file_checkboxes()
        
        git_status = self.current_project.git_status
        
        # Track all unique files
        all_files = set()
        staged_files = set(git_status.get('staged', []))
        modified_files = set(git_status.get('modified', []))
        untracked_files = set(git_status.get('untracked', []))
        
        # Add all modified, staged, and untracked files to the set
        all_files.update(staged_files)
        all_files.update(modified_files)
        all_files.update(untracked_files)
        
        # Create checkboxes for each file
        for file_path in sorted(all_files):
            is_staged = file_path in staged_files
            
            checkbox = QCheckBox(file_path)
            checkbox.setChecked(is_staged)
            checkbox.stateChanged.connect(lambda state, path=file_path: self.on_file_staging_changed(state, path))
            
            # Set appropriate style
            if is_staged:
                checkbox.setStyleSheet("QCheckBox { color: #4CAF50; }")
            elif file_path in untracked_files:
                checkbox.setStyleSheet("QCheckBox { color: #FF5722; }")
            else:
                checkbox.setStyleSheet("QCheckBox { color: #666666; }")
            
            self.files_layout.addWidget(checkbox)
            self.file_checkboxes[file_path] = checkbox
        
        # Update the files count label
        self.files_label.setText(f"Modified Files ({len(all_files)})")
    
    def on_file_staging_changed(self, state, file_path):
        """Handle checkbox state changes for file staging"""
        if not self.current_project:
            return
        
        is_checked = state == Qt.CheckState.Checked.value
        
        if is_checked:
            # Show status message
            self.set_status_message(f"Staging {file_path}...")
            
            # Stage the file
            success = self.git_service.stage_file(self.current_project.path, file_path)
            if success:
                self.file_checkboxes[file_path].setStyleSheet("QCheckBox { color: #4CAF50; }")
                self.set_status_message(f"Staged {file_path}")
            else:
                # Revert the checkbox if staging failed
                self.file_checkboxes[file_path].setChecked(False)
                self.set_status_message(f"Failed to stage {file_path}")
                QMessageBox.critical(self, "Error", f"Failed to stage file: {file_path}")
        else:
            # Show status message
            self.set_status_message(f"Unstaging {file_path}...")
            
            # Unstage the file
            success = self.git_service.unstage_file(self.current_project.path, file_path)
            if success:
                # Set appropriate style based on whether it's untracked
                if file_path in self.current_project.git_status.get('untracked', []):
                    self.file_checkboxes[file_path].setStyleSheet("QCheckBox { color: #FF5722; }")
                else:
                    self.file_checkboxes[file_path].setStyleSheet("QCheckBox { color: #666666; }")
                self.set_status_message(f"Unstaged {file_path}")
            else:
                # Revert the checkbox if unstaging failed
                self.file_checkboxes[file_path].setChecked(True)
                self.set_status_message(f"Failed to unstage {file_path}")
                QMessageBox.critical(self, "Error", f"Failed to unstage file: {file_path}")
        
        # Refresh Git status
        self.refresh_git_status()
    
    def on_stage_all(self):
        """Stage all modified files"""
        if not self.current_project:
            return
        
        self.set_status_message("Staging all files...")
        success = self.git_service.stage_all(self.current_project.path)
        if success:
            self.refresh_git_status()
            self.set_status_message("All files staged")
        else:
            self.set_status_message("Failed to stage all files")
            QMessageBox.critical(self, "Error", "Failed to stage all files")
    
    def on_unstage_all(self):
        """Unstage all files"""
        if not self.current_project:
            return
        
        self.set_status_message("Unstaging all files...")
        success = self.git_service.unstage_all(self.current_project.path)
        if success:
            self.refresh_git_status()
            self.set_status_message("All files unstaged")
        else:
            self.set_status_message("Failed to unstage all files")
            QMessageBox.critical(self, "Error", "Failed to unstage all files")
    
    def on_refresh(self):
        """Refresh Git status (for Actions section button)"""
        if not self.current_project:
            return
        
        self.set_status_message("Refreshing Git status...")
        self.refresh_git_status()
    
    def on_commit(self):
        """Commit changes"""
        if not self.current_project:
            return
        
        message = self.commit_message.toPlainText().strip()
        if not message:
            QMessageBox.critical(self, "Error", "Please enter a commit message")
            return
        
        self.set_status_message("Committing changes...")
        success, output = self.git_service.commit(self.current_project.path, message)
        if success:
            self.commit_message.clear()
            self.refresh_git_status()
            self.update_recent_commits()
            self.set_status_message("Changes committed successfully")
            QMessageBox.information(self, "Success", "Changes committed successfully")
        else:
            self.set_status_message("Failed to commit changes")
            QMessageBox.critical(self, "Error", f"Failed to commit changes:\n{output}")
    
    def on_commit_push(self):
        """Commit and push changes"""
        if not self.current_project:
            return
        
        message = self.commit_message.toPlainText().strip()
        if not message:
            QMessageBox.critical(self, "Error", "Please enter a commit message")
            return
        
        self.set_status_message("Committing and pushing changes...")
        success, output = self.git_service.commit(self.current_project.path, message, push=True)
        if success:
            self.commit_message.clear()
            self.refresh_git_status()
            self.update_recent_commits()
            self.set_status_message("Changes committed and pushed successfully")
            QMessageBox.information(self, "Success", "Changes committed and pushed successfully")
        else:
            self.set_status_message("Failed to commit and push changes")
            QMessageBox.critical(self, "Error", f"Failed to commit and push changes:\n{output}")
    
    def on_pull(self):
        """Pull changes from remote"""
        if not self.current_project:
            return
        
        self.set_status_message("Pulling changes...")
        success, output = self.git_service.pull(self.current_project.path)
        if success:
            self.refresh_git_status()
            self.update_recent_commits()
            self.set_status_message("Changes pulled successfully")
            QMessageBox.information(self, "Success", "Changes pulled successfully")
        else:
            self.set_status_message("Failed to pull changes")
            QMessageBox.critical(self, "Error", f"Failed to pull changes:\n{output}")
    
    def on_push(self):
        """Push commits to remote"""
        if not self.current_project:
            return
        
        self.set_status_message("Pushing commits...")
        success, output = self.git_service.push(self.current_project.path)
        if success:
            self.update_recent_commits()
            self.set_status_message("Commits pushed successfully")
            QMessageBox.information(self, "Success", "Commits pushed successfully")
        else:
            self.set_status_message("Failed to push commits")
            QMessageBox.critical(self, "Error", f"Failed to push commits:\n{output}")
    
    def on_stash(self):
        """Stash changes"""
        if not self.current_project:
            return
        
        self.set_status_message("Stashing changes...")
        success, output = self.git_service.stash(self.current_project.path)
        if success:
            self.refresh_git_status()
            self.set_status_message("Changes stashed successfully")
            QMessageBox.information(self, "Success", "Changes stashed successfully")
        else:
            self.set_status_message("Failed to stash changes")
            QMessageBox.critical(self, "Error", f"Failed to stash changes:\n{output}")
    
    def on_pop_stash(self):
        """Pop stashed changes"""
        if not self.current_project:
            return
        
        self.set_status_message("Applying stashed changes...")
        success, output = self.git_service.pop_stash(self.current_project.path)
        if success:
            self.refresh_git_status()
            self.set_status_message("Stashed changes applied successfully")
            QMessageBox.information(self, "Success", "Stashed changes applied successfully")
        else:
            self.set_status_message("Failed to apply stashed changes")
            QMessageBox.critical(self, "Error", f"Failed to pop stash:\n{output}")
    
    def update_recent_commits(self):
        """Update the recent commits display"""
        if not self.current_project:
            return
        
        self.set_status_message("Fetching recent commits...")
        success, commits = self.git_service.get_recent_commits(self.current_project.path)
        if success:
            self.recent_commits.setText(commits)
            self.set_status_message("Recent commits updated")
        else:
            self.recent_commits.setText("Unable to retrieve commit history")
            self.set_status_message("Failed to retrieve commit history")
    
    def refresh_git_status(self, show_message=True):
        """Refresh Git status and update UI"""
        if not self.current_project:
            return
        
        self.current_project.refresh_git_status(self.git_service)
        
        # Update branch label
        self.branch_label.setText(f"Current Branch: {self.current_project.current_branch}")
        
        # Update file checkboxes
        self.update_file_checkboxes()
        
        # Show status message if requested
        if show_message:
            self.set_status_message("Git status refreshed")
    
    def update_for_project(self, project):
        """Update the Git panel for the selected project"""
        debug_print(f"GitPanel.update_for_project called for project: {project.name if project else 'None'}")
        self.current_project = project
        
        if project:
            debug_print(f"Updating Git panel for project: {project.name}")
            debug_print(f"Project path: {project.path}")
            debug_print(f"Project is_git_repo: {project.is_git_repo}")
            
            self.set_status_message(f"Loading Git info for {project.name}...")
            
            try:
                # Check if it's a Git repository and load Git info if needed
                if not project.is_git_repo:
                    debug_print(f"Loading Git info for project: {project.name}")
                    project.load_git_info(self.git_service)
                    debug_print(f"After load_git_info, is_git_repo: {project.is_git_repo}")
                
                if project.is_git_repo:
                    # Enable the panel
                    debug_print(f"Enabling Git panel for project: {project.name}")
                    self.setEnabled(True)
                    self.setVisible(True)  # Ensure the panel is visible
                    
                    # Update UI elements
                    self.branch_label.setText(f"Current Branch: {project.current_branch}")
                    self.update_file_checkboxes()
                    self.update_recent_commits()
                    
                    # Update branch list
                    self.update_branch_list()
                    
                    # Force a repaint to ensure UI updates
                    self.repaint()
                    
                    self.set_status_message("Git repository loaded successfully")
                    debug_print(f"Git panel enabled and updated for {project.name}")
                else:
                    # Disable the panel if it's not a Git repo
                    debug_print(f"Project {project.name} is not a Git repository")
                    self.setEnabled(False)
                    self.branch_label.setText("Not a Git repository")
                    self.clear_file_checkboxes()
                    self.files_label.setText("Modified Files (0)")
                    self.recent_commits.setText("")
                    self.set_status_message("Not a Git repository")
            except Exception as e:
                # Handle any unexpected errors
                debug_print(f"Error updating Git panel: {str(e)}")
                self.setEnabled(False)
                self.branch_label.setText("Error accessing Git repository")
                self.clear_file_checkboxes()
                self.files_label.setText("Modified Files (0)")
                self.recent_commits.setText("Error: Unable to access Git repository information")
                self.set_status_message("Error accessing Git repository")
        else:
            debug_print("No project selected, disabling Git panel")
            # Clear/disable the UI when no project is selected
            self.setEnabled(False)
            self.branch_label.setText("No project selected")
            self.clear_file_checkboxes()
            self.files_label.setText("Modified Files (0)")
            self.recent_commits.setText("")
            self.set_status_message("")
    
    def set_status_message(self, message, duration=3000):
        """Set a temporary status message that disappears after duration ms"""
        self.status_message.setText(message)
        
        # Clear any existing timer
        if self.status_timer:
            self.status_timer.stop()
        
        # Set up timer to clear the message
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(lambda: self.status_message.setText(""))
        self.status_timer.setSingleShot(True)
        self.status_timer.start(duration)
    
    def update_branch_list(self):
        """Update the branch dropdown with available branches"""
        if not self.current_project:
            return
        
        self.set_status_message("Fetching branches...")
        
        # Remember current text before clearing
        current_selection = self.branch_dropdown.currentText()
        
        # Get branches using the GitService
        success, branches = self.git_service.get_branches(self.current_project.path)
        
        if success:
            # Block signals to prevent triggering on_branch_selection_changed during update
            self.branch_dropdown.blockSignals(True)
            
            # Clear existing items
            self.branch_dropdown.clear()
            
            # Add local branches to dropdown
            self.branch_dropdown.addItems(branches['local'])
            
            # Select current branch
            current_branch = branches['current']
            current_index = self.branch_dropdown.findText(current_branch)
            if current_index >= 0:
                self.branch_dropdown.setCurrentIndex(current_index)
            elif self.branch_dropdown.count() > 0:
                self.branch_dropdown.setCurrentIndex(0)
                
            # Re-enable signals
            self.branch_dropdown.blockSignals(False)
            
            count = len(branches['local'])
            self.set_status_message(f"Found {count} branches")
        else:
            debug_print(f"Error getting branches: {branches}")
            self.set_status_message("Error fetching branches")
    
    def on_checkout_branch(self):
        """Checkout the selected branch"""
        if not self.current_project:
            return
        
        selected_branch = self.branch_dropdown.currentText()
        if not selected_branch:
            return
        
        self.set_status_message(f"Checking out {selected_branch}...")
        
        # Use GitService to checkout branch
        success, message = self.git_service.checkout_branch(self.current_project.path, selected_branch)
        
        if success:
            # Update UI
            self.refresh_git_status()
            self.set_status_message(f"Switched to branch '{selected_branch}'")
            QMessageBox.information(self, "Branch Checkout", f"Successfully switched to branch '{selected_branch}'")
        else:
            error_msg = message
            debug_print(f"Error checking out branch: {error_msg}")
            self.set_status_message("Error switching branches")
            QMessageBox.critical(self, "Branch Checkout Error", f"Failed to checkout branch:\n{error_msg}")
    
    def on_branch_selection_changed(self, index):
        """Handle branch selection changes"""
        if not self.current_project or index < 0:
            return
        
        selected_branch = self.branch_dropdown.currentText()
        current_branch = self.current_project.current_branch
        
        # Update UI to show if the selected branch is different from current
        if selected_branch != current_branch:
            self.set_status_message(f"Selected branch '{selected_branch}' (click Checkout to switch)")
    
    def on_create_branch(self):
        """Create a new branch"""
        if not self.current_project:
            return
        
        # Show an input dialog to get the branch name
        branch_name, ok = QInputDialog.getText(
            self, "Create New Branch", 
            "Enter the name for the new branch:",
            QLineEdit.EchoMode.Normal
        )
        
        if not ok or not branch_name.strip():
            return
        
        # Clean up the branch name
        branch_name = branch_name.strip()
        
        # Confirm with the user
        reply = QMessageBox.question(
            self, "Create Branch", 
            f"Create and checkout branch '{branch_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.set_status_message(f"Creating branch '{branch_name}'...")
        
        # Create the branch
        success, message = self.git_service.create_branch(self.current_project.path, branch_name)
        
        if success:
            # Update UI
            self.refresh_git_status()
            self.update_branch_list()
            self.set_status_message(f"Created and switched to branch '{branch_name}'")
            QMessageBox.information(self, "Branch Created", f"Successfully created and switched to branch '{branch_name}'")
        else:
            error_msg = message
            debug_print(f"Error creating branch: {error_msg}")
            self.set_status_message("Error creating branch")
            QMessageBox.critical(self, "Branch Creation Error", f"Failed to create branch:\n{error_msg}")
    
    def refresh_git_panel(self):
        """Refresh both Git status and branch list"""
        if not self.current_project:
            return
            
        self.set_status_message("Refreshing Git status and branches...")
        
        # First refresh Git status
        self.refresh_git_status(show_message=False)
        
        # Then update branch list
        self.update_branch_list()
        
        self.set_status_message("Git status and branches refreshed") 