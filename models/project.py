import os
import json
import shutil
from utils.debug import debug_print
from config import PROJECTS_DB_DIR

class Project:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.info = {}
        self.scripts = {}
        self.is_git_repo = False
        self.git_status = None
        self.current_branch = "Unknown"
        # Database paths for JSON files
        self.db_dir = os.path.join(PROJECTS_DB_DIR, self.name)
        self.db_info_path = os.path.join(self.db_dir, 'project_info.json')
        self.db_scripts_path = os.path.join(self.db_dir, 'scripts.json')
    
    def load_info(self):
        """Load project information from project_info.json"""
        # Prioritize database version if it exists
        if os.path.exists(self.db_info_path):
            try:
                with open(self.db_info_path, 'r') as f:
                    self.info = json.load(f)
                debug_print(f"Loaded project info from database: {self.db_info_path}")
                return True
            except Exception as e:
                debug_print(f"Error loading project info from database: {str(e)}")
        
        # Fall back to project directory version
        info_file = os.path.join(self.path, 'project_info.json')
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r') as f:
                    self.info = json.load(f)
                debug_print(f"Loaded project info from project directory: {info_file}")
                
                # If database dir doesn't exist, initialize it by syncing from project
                if not os.path.exists(self.db_dir):
                    self.sync_to_database()
                
                return True
            except Exception as e:
                debug_print(f"Error loading project info: {str(e)}")
        return False
    
    def load_scripts(self):
        """Load project scripts from scripts.json"""
        # Prioritize database version if it exists
        if os.path.exists(self.db_scripts_path):
            try:
                with open(self.db_scripts_path, 'r') as f:
                    scripts_data = json.load(f)
                    self.scripts = scripts_data.get('scripts', {})
                debug_print(f"Loaded scripts from database: {self.db_scripts_path}")
                return True
            except Exception as e:
                debug_print(f"Error loading scripts from database: {str(e)}")
        
        # Fall back to project directory version
        scripts_file = os.path.join(self.path, 'scripts.json')
        if os.path.exists(scripts_file):
            try:
                with open(scripts_file, 'r') as f:
                    scripts_data = json.load(f)
                    self.scripts = scripts_data.get('scripts', {})
                debug_print(f"Loaded scripts from project directory: {scripts_file}")
                
                # If database dir doesn't exist, initialize it by syncing from project
                if not os.path.exists(self.db_dir):
                    self.sync_to_database()
                
                return True
            except Exception as e:
                debug_print(f"Error loading scripts: {str(e)}")
        return False
    
    def sync_to_database(self):
        """Sync JSON files from project directory to database"""
        try:
            # Create database directory if it doesn't exist
            os.makedirs(self.db_dir, exist_ok=True)
            
            # Sync project_info.json
            project_info_file = os.path.join(self.path, 'project_info.json')
            if os.path.exists(project_info_file):
                shutil.copy2(project_info_file, self.db_info_path)
                debug_print(f"Synced project_info.json to database: {self.db_info_path}")
            
            # Sync scripts.json
            scripts_file = os.path.join(self.path, 'scripts.json')
            if os.path.exists(scripts_file):
                shutil.copy2(scripts_file, self.db_scripts_path)
                debug_print(f"Synced scripts.json to database: {self.db_scripts_path}")
            
            return True
        except Exception as e:
            debug_print(f"Error syncing to database: {str(e)}")
            return False
    
    def sync_from_database(self):
        """Sync JSON files from database to project directory"""
        try:
            # Sync project_info.json
            if os.path.exists(self.db_info_path):
                project_info_file = os.path.join(self.path, 'project_info.json')
                shutil.copy2(self.db_info_path, project_info_file)
                debug_print(f"Synced project_info.json from database to project: {project_info_file}")
            
            # Sync scripts.json
            if os.path.exists(self.db_scripts_path):
                scripts_file = os.path.join(self.path, 'scripts.json')
                shutil.copy2(self.db_scripts_path, scripts_file)
                debug_print(f"Synced scripts.json from database to project: {scripts_file}")
            
            return True
        except Exception as e:
            debug_print(f"Error syncing from database: {str(e)}")
            return False

    def get_json_file_path(self, file_name, prefer_db=True):
        """Get the appropriate path for a JSON file based on preference"""
        if file_name == "project_info.json":
            db_path = self.db_info_path
        elif file_name == "scripts.json":
            db_path = self.db_scripts_path
        else:
            # For any other JSON file, use project directory
            return os.path.join(self.path, file_name)
        
        # Determine which path to return based on preference and existence
        project_path = os.path.join(self.path, file_name)
        
        if prefer_db and os.path.exists(db_path):
            return db_path
        elif os.path.exists(project_path):
            return project_path
        elif os.path.exists(db_path):
            return db_path
        else:
            return project_path  # Default to project path even if it doesn't exist yet
    
    def load_git_info(self, git_service):
        """Load Git information for the project"""
        debug_print(f"Project.load_git_info called for {self.name} at {self.path}")
        self.is_git_repo = git_service.is_git_repo(self.path)
        debug_print(f"Project.load_git_info: is_git_repo = {self.is_git_repo}")
        
        if self.is_git_repo:
            self.current_branch = git_service.get_current_branch(self.path)
            debug_print(f"Project.load_git_info: current_branch = {self.current_branch}")
            
            self.git_status = git_service.get_status(self.path)
            debug_print(f"Project.load_git_info: git_status = {self.git_status}")
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
        debug_print(f"Project.refresh_git_status called for {self.name} at {self.path}")
        if self.is_git_repo or git_service.is_git_repo(self.path):
            self.is_git_repo = True
            self.current_branch = git_service.get_current_branch(self.path)
            debug_print(f"Project.refresh_git_status: current_branch = {self.current_branch}")
            
            self.git_status = git_service.get_status(self.path)
            debug_print(f"Project.refresh_git_status: git_status = {self.git_status}")
            return True
        
        return False 