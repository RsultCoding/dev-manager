from PyQt6.QtWidgets import QApplication
import sys
import os
from app import DevSupportApp
from utils.debug import debug_print
from services.git_service import GitService

def main():
    debug_print("Starting application")
    
    # Check if the current directory is a Git repository
    current_dir = os.path.dirname(os.path.abspath(__file__))
    git_service = GitService()
    is_repo = git_service.is_git_repo(current_dir)
    debug_print(f"Current directory is Git repository: {is_repo}")
    
    if is_repo:
        branch = git_service.get_current_branch(current_dir)
        debug_print(f"Current branch: {branch}")
        
        status = git_service.get_status(current_dir)
        debug_print(f"Git status: {status}")
    
    # Start the application
    app = QApplication(sys.argv)
    window = DevSupportApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
