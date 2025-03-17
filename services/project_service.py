import os
import json
import time
from config import SITES_DIR, CACHE_FILE, RESTRICTED_COMMANDS
from models.project import Project
from utils.debug import debug_print

class ProjectService:
    def __init__(self):
        self.projects = []
        self.is_scanning = False
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
                        else:
                            debug_print(f"Skipping non-existent project: {path}")
                
                debug_print(f"Loaded {len(self.projects)} projects from cache")
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