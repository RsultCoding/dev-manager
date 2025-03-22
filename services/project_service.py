import os
import json
import time
import shutil
from config import SITES_DIR, CACHE_FILE, RESTRICTED_COMMANDS, PROJECTS_DB_DIR
from models.project import Project
from utils.debug import debug_print

class ProjectService:
    def __init__(self):
        self.projects = []
        self.is_scanning = False
        # Ensure database directory exists
        os.makedirs(PROJECTS_DB_DIR, exist_ok=True)
        self.load_cached_projects()
    
    def load_cached_projects(self):
        """Load projects from the cache file"""
        self.projects = []
        
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache_data = json.load(f)
                    project_paths = cache_data.get('projects', [])
                    
                    # Filter out non-existent projects
                    for path in project_paths:
                        if os.path.exists(path):
                            project = Project(path)
                            self.projects.append(project)
                            debug_print(f"Added project from cache: {project.name} at {project.path}")
                        else:
                            debug_print(f"Skipping non-existent project: {path}")
                
                debug_print(f"Loaded {len(self.projects)} projects from cache")
                
                # Initialize Git for the current project (dev-manager)
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                debug_print(f"Current directory: {current_dir}")
                
                # Check if the current directory is in the projects list
                current_project = None
                for project in self.projects:
                    if project.path == current_dir:
                        current_project = project
                        break
                
                if current_project:
                    debug_print(f"Found current project in cache: {current_project.name}")
                    from services.git_service import GitService
                    git_service = GitService()
                    current_project.load_git_info(git_service)
                    debug_print(f"Current project is Git repo: {current_project.is_git_repo}")
                else:
                    debug_print("Current directory not found in projects list")
                
                return True
            except Exception as e:
                debug_print(f"Error loading cache: {str(e)}")
        
        return False
    
    def save_cache(self):
        """Save projects to the cache file"""
        try:
            # Ensure projects exist
            existing_projects = [p.path for p in self.projects if os.path.exists(p.path)]
            
            # Prepare cache data
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
            return False
    
    def scan_projects(self, callback=None):
        """
        Scan for projects in the SITES_DIR
        
        Args:
            callback: Optional callback function to update UI
        """
        if self.is_scanning:
            return False
        
        self.is_scanning = True
        found_projects = []
        
        try:
            debug_print(f"Starting scan in {SITES_DIR}")
            
            # Update UI if callback provided
            if callback:
                callback("Scanning started...")
            
            # Scan up to 3 directory levels deep (SITES_DIR + 2 more levels)
            for root, dirs, files in os.walk(SITES_DIR):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Calculate current depth (relative to SITES_DIR)
                path_parts = os.path.relpath(root, SITES_DIR).split(os.sep)
                current_depth = len(path_parts)
                
                # Only process directories up to 3 levels deep (SITES_DIR + 2 more levels)
                if current_depth > 3:
                    # Remove all subdirectories to prevent further traversal
                    dirs[:] = []
                    continue
                
                # Check if this directory is a project
                if 'project_info.json' in files:
                    project_path = root
                    found_projects.append(project_path)
                    
                    # Update UI if callback provided
                    if callback:
                        project_name = os.path.basename(project_path)
                        callback(f"Found project: {project_name}")
                    
                    # Ensure the project's database directory exists
                    project_name = os.path.basename(project_path)
                    project_db_dir = os.path.join(PROJECTS_DB_DIR, project_name)
                    os.makedirs(project_db_dir, exist_ok=True)
                    
                    # Copy JSON files to database if they don't exist or if project version is newer
                    project_info_file = os.path.join(project_path, 'project_info.json')
                    db_info_file = os.path.join(project_db_dir, 'project_info.json')
                    
                    if os.path.exists(project_info_file):
                        if not os.path.exists(db_info_file) or os.path.getmtime(project_info_file) > os.path.getmtime(db_info_file):
                            shutil.copy2(project_info_file, db_info_file)
                            debug_print(f"Copied {project_info_file} to database")
                    
                    # Copy scripts.json if it exists
                    if 'scripts.json' in files:
                        scripts_file = os.path.join(project_path, 'scripts.json')
                        db_scripts_file = os.path.join(project_db_dir, 'scripts.json')
                        
                        if os.path.exists(scripts_file):
                            if not os.path.exists(db_scripts_file) or os.path.getmtime(scripts_file) > os.path.getmtime(db_scripts_file):
                                shutil.copy2(scripts_file, db_scripts_file)
                                debug_print(f"Copied {scripts_file} to database")
            
            # Create Project objects
            self.projects = [Project(path) for path in found_projects]
            
            # Save to cache
            self.save_cache()
            
            debug_print(f"Scan complete. Found {len(self.projects)} projects.")
            
            # Update UI if callback provided
            if callback:
                callback(f"Scan complete. Found {len(self.projects)} projects.")
            
            return True
        except Exception as e:
            debug_print(f"Error during scan: {str(e)}")
            if callback:
                callback(f"Error during scan: {str(e)}")
            return False
        finally:
            self.is_scanning = False
    
    def validate_script(self, command):
        """
        Validate a script command for security
        
        Returns:
            (bool, str): (is_valid, reason)
        """
        # Check for restricted commands
        for restricted in RESTRICTED_COMMANDS:
            if restricted in command:
                return False, f"Command contains restricted term: {restricted}"
        
        # Additional security checks could be added here
        
        return True, "Valid command"
    
    def get_json_file_differences(self, project, file_name):
        """
        Compare project and database versions of a JSON file
        
        Args:
            project: Project object
            file_name: Name of the JSON file to compare
            
        Returns:
            tuple: (has_differences, database_newer, project_only, database_only, message)
                has_differences: True if files are different
                database_newer: True if database file is newer
                project_only: True if file exists only in project
                database_only: True if file exists only in database
                message: Description of the difference
        """
        try:
            project_file_path = os.path.join(project.path, file_name)
            
            # Get database file path
            db_file_path = None
            if file_name == "project_info.json":
                db_file_path = project.db_info_path
            elif file_name == "scripts.json":
                db_file_path = project.db_scripts_path
            
            if not db_file_path:
                return False, False, True, False, f"No database path defined for {file_name}"
            
            # Check file existence
            project_exists = os.path.exists(project_file_path)
            db_exists = os.path.exists(db_file_path)
            
            if not project_exists and not db_exists:
                return False, False, False, False, f"Neither project nor database has {file_name}"
            
            if project_exists and not db_exists:
                return True, False, True, False, f"File {file_name} exists only in project"
            
            if not project_exists and db_exists:
                return True, True, False, True, f"File {file_name} exists only in database"
            
            # Both files exist - compare them
            with open(project_file_path, 'r') as f:
                project_data = json.load(f)
            
            with open(db_file_path, 'r') as f:
                db_data = json.load(f)
            
            # Compare the file contents
            if project_data == db_data:
                # Files are identical in content
                # Check which is newer
                project_mtime = os.path.getmtime(project_file_path)
                db_mtime = os.path.getmtime(db_file_path)
                
                if db_mtime > project_mtime:
                    return False, True, False, False, f"Files are identical but database is newer"
                else:
                    return False, False, False, False, f"Files are identical"
            else:
                # Files have different content
                # Check which is newer
                project_mtime = os.path.getmtime(project_file_path)
                db_mtime = os.path.getmtime(db_file_path)
                
                if db_mtime > project_mtime:
                    return True, True, False, False, f"Files have different content and database is newer"
                else:
                    return True, False, False, False, f"Files have different content and project is newer"
        
        except Exception as e:
            debug_print(f"Error comparing JSON files: {str(e)}")
            return False, False, False, False, f"Error comparing files: {str(e)}" 