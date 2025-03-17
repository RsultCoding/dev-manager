import os
import json
from utils.debug import debug_print

class Project:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.info = {}
        self.scripts = {}
        self.is_git_repo = False
        self.git_status = None
        self.current_branch = "Unknown"
    
    def load_info(self):
        """Load project information from project_info.json"""
        info_file = os.path.join(self.path, 'project_info.json')
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r') as f:
                    self.info = json.load(f)
                return True
            except Exception as e:
                debug_print(f"Error loading project info: {str(e)}")
        return False
    
    def load_scripts(self):
        """Load project scripts from scripts.json"""
        scripts_file = os.path.join(self.path, 'scripts.json')
        if os.path.exists(scripts_file):
            try:
                with open(scripts_file, 'r') as f:
                    scripts_data = json.load(f)
                    self.scripts = scripts_data.get('scripts', {})
                return True
            except Exception as e:
                debug_print(f"Error loading scripts: {str(e)}")
        return False
    
    def load_git_info(self, git_service):
        """Load Git information for the project"""
        self.is_git_repo = git_service.is_git_repo(self.path)
        
        if self.is_git_repo:
            self.current_branch = git_service.get_current_branch(self.path)
            self.git_status = git_service.get_status(self.path)
            return True
        
        return False
    
    def get_modified_files_count(self):
        """Get the total count of modified files (staged, unstaged, and untracked)"""
        if not self.git_status:
            return 0
        
        count = 0
        count += len(self.git_status.get('staged', []))
        
        # Only count files that are modified but not staged
        for file in self.git_status.get('modified', []):
            if file not in self.git_status.get('staged', []):
                count += 1
                
        count += len(self.git_status.get('untracked', []))
        
        return count
    
    def refresh_git_status(self, git_service):
        """Refresh Git status information"""
        if self.is_git_repo or git_service.is_git_repo(self.path):
            self.is_git_repo = True
            self.current_branch = git_service.get_current_branch(self.path)
            self.git_status = git_service.get_status(self.path)
            return True
        
        return False 