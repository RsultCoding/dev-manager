#!/usr/bin/env python3
"""Test script to verify Git functionality"""

import os
import sys
from services.git_service import GitService
from utils.debug import debug_print

def test_git_service():
    """Test the GitService with the current directory"""
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    debug_print(f"Testing Git service in: {current_dir}")
    
    # Create Git service
    git_service = GitService()
    
    # Check if directory is a Git repository
    is_repo = git_service.is_git_repo(current_dir)
    debug_print(f"Is Git repository: {is_repo}")
    
    if is_repo:
        # Get current branch
        branch = git_service.get_current_branch(current_dir)
        debug_print(f"Current branch: {branch}")
        
        # Get Git status
        status = git_service.get_status(current_dir)
        debug_print(f"Git status: {status}")
        
        # Get branches
        success, branches = git_service.get_branches(current_dir)
        if success:
            debug_print(f"Branches: {branches}")
        else:
            debug_print(f"Failed to get branches: {branches}")
            
        # Get recent commits
        success, commits = git_service.get_recent_commits(current_dir)
        if success:
            debug_print(f"Recent commits:\n{commits}")
        else:
            debug_print(f"Failed to get recent commits: {commits}")
    else:
        debug_print("Not a Git repository. Exiting.")

if __name__ == "__main__":
    debug_print("Starting Git service test")
    test_git_service()
    debug_print("Git service test complete") 