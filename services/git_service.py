import os
import subprocess
from utils.debug import debug_print
from config import SUBPROCESS_TIMEOUT

class GitService:
    def __init__(self):
        pass
    
    def is_git_repo(self, project_path):
        """Check if a project directory is a Git repository"""
        if not project_path or not os.path.exists(project_path):
            debug_print(f"Invalid project path: {project_path}")
            return False
            
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            # Check if the output is "true" (ignoring whitespace)
            is_repo = result.returncode == 0 and result.stdout.strip() == "true"
            
            if is_repo:
                debug_print(f"Valid Git repository found at: {project_path}")
            else:
                debug_print(f"Not a Git repository: {project_path}")
                
            return is_repo
        except Exception as e:
            debug_print(f"Error checking Git repo: {str(e)}")
            return False
    
    def get_current_branch(self, project_path):
        """Get the current branch name of a Git repository"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception as e:
            debug_print(f"Error getting current branch: {str(e)}")
            return "error"
    
    def get_status(self, project_path):
        """Get the status of a Git repository
        
        Returns:
            dict: Dictionary with status information
                - 'modified': List of modified files (not staged)
                - 'staged': List of staged files
                - 'untracked': List of untracked files
        """
        status = {
            'modified': [],
            'staged': [],
            'untracked': []
        }
        
        if not project_path or not os.path.exists(project_path):
            debug_print(f"Invalid project path for git status: {project_path}")
            return status
            
        try:
            # Get status in porcelain format for easier parsing
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue
                    
                    # Parse status line
                    status_code = line[:2]
                    file_path = line[3:].strip()
                    
                    # Handle different status codes
                    # First character: index/staged status
                    # Second character: working tree status
                    index_status = status_code[0]
                    worktree_status = status_code[1]
                    
                    # Staged files (changes in index)
                    if index_status in ['M', 'A', 'D', 'R', 'C']:
                        status['staged'].append(file_path)
                    
                    # Modified files (changes in working tree)
                    if worktree_status in ['M', 'D']:
                        status['modified'].append(file_path)
                    
                    # Untracked files
                    if status_code == '??':
                        status['untracked'].append(file_path)
                
                debug_print(f"Git status found {len(status['staged'])} staged, " +
                           f"{len(status['modified'])} modified, " +
                           f"{len(status['untracked'])} untracked files")
                return status
            
            debug_print(f"Error getting Git status: {result.stderr}")
            return status
            
        except Exception as e:
            debug_print(f"Error getting Git status: {str(e)}")
            return status
    
    def stage_file(self, project_path, file_path):
        """Stage a single file"""
        try:
            result = subprocess.run(
                ["git", "add", file_path],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0
        except Exception as e:
            debug_print(f"Error staging file: {str(e)}")
            return False
    
    def unstage_file(self, project_path, file_path):
        """Unstage a single file"""
        try:
            result = subprocess.run(
                ["git", "reset", "HEAD", file_path],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0
        except Exception as e:
            debug_print(f"Error unstaging file: {str(e)}")
            return False
    
    def stage_all(self, project_path):
        """Stage all modified files"""
        try:
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0
        except Exception as e:
            debug_print(f"Error staging all files: {str(e)}")
            return False
    
    def unstage_all(self, project_path):
        """Unstage all files"""
        try:
            result = subprocess.run(
                ["git", "reset", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0
        except Exception as e:
            debug_print(f"Error unstaging all files: {str(e)}")
            return False
    
    def commit(self, project_path, message, push=False):
        """Commit changes with the given message"""
        try:
            # Perform commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            commit_success = commit_result.returncode == 0
            
            # Push if requested and commit was successful
            if push and commit_success:
                push_result = subprocess.run(
                    ["git", "push"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIMEOUT
                )
                
                # Return combined output
                return commit_success and push_result.returncode == 0, \
                       commit_result.stdout + "\n" + push_result.stdout
            
            return commit_success, commit_result.stdout
            
        except Exception as e:
            debug_print(f"Error committing changes: {str(e)}")
            return False, str(e)
    
    def pull(self, project_path):
        """Pull changes from remote"""
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            debug_print(f"Error pulling changes: {str(e)}")
            return False, str(e)
    
    def push(self, project_path):
        """Push commits to remote repository"""
        try:
            result = subprocess.run(
                ["git", "push"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            debug_print(f"Error pushing changes: {str(e)}")
            return False, str(e)
    
    def stash(self, project_path):
        """Stash changes"""
        try:
            result = subprocess.run(
                ["git", "stash"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            debug_print(f"Error stashing changes: {str(e)}")
            return False, str(e)
    
    def pop_stash(self, project_path):
        """Pop stashed changes"""
        try:
            result = subprocess.run(
                ["git", "stash", "pop"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            debug_print(f"Error popping stash: {str(e)}")
            return False, str(e)
    
    def get_recent_commits(self, project_path, count=5):
        """Get recent commits"""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--pretty=format:%h %cr: %s"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                return True, result.stdout
            return False, result.stderr
            
        except Exception as e:
            debug_print(f"Error getting recent commits: {str(e)}")
            return False, str(e)
    
    def get_branches(self, project_path):
        """Get available branches
        
        Returns:
            (bool, dict): (success, data)
                - data: Dictionary with branch information when successful
                    - 'current': Current branch name
                    - 'local': List of local branches
                    - 'remote': List of remote branches
                - data: Error message when failed
        """
        try:
            # Get local branches
            result = subprocess.run(
                ["git", "branch", "--list"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            if result.returncode != 0:
                return False, result.stderr
            
            # Parse branches
            branches = {
                'current': '',
                'local': [],
                'remote': []
            }
            
            for line in result.stdout.splitlines():
                branch = line.strip()
                if branch.startswith('*'):
                    # Current branch
                    branch_name = branch[1:].strip()
                    branches['current'] = branch_name
                    branches['local'].append(branch_name)
                else:
                    branches['local'].append(branch)
            
            # Get remote branches (optional)
            try:
                remote_result = subprocess.run(
                    ["git", "branch", "-r"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIMEOUT
                )
                
                if remote_result.returncode == 0:
                    for line in remote_result.stdout.splitlines():
                        remote_branch = line.strip()
                        if remote_branch and not remote_branch.startswith('*'):
                            branches['remote'].append(remote_branch)
            except Exception as e:
                debug_print(f"Error getting remote branches: {str(e)}")
                # Continue without remote branches
            
            return True, branches
            
        except Exception as e:
            debug_print(f"Error getting branches: {str(e)}")
            return False, str(e)
    
    def checkout_branch(self, project_path, branch_name):
        """Checkout a branch
        
        Args:
            project_path: Path to the project
            branch_name: Name of the branch to checkout
            
        Returns:
            (bool, str): (success, message)
        """
        try:
            result = subprocess.run(
                ["git", "checkout", branch_name],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                return True, result.stdout
            return False, result.stderr
            
        except Exception as e:
            debug_print(f"Error checking out branch: {str(e)}")
            return False, str(e)
            
    def create_branch(self, project_path, branch_name, checkout=True):
        """Create a new branch
        
        Args:
            project_path: Path to the project
            branch_name: Name of the new branch
            checkout: Whether to checkout the new branch after creating it
            
        Returns:
            (bool, str): (success, message)
        """
        try:
            if checkout:
                # Create and checkout in one step
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIMEOUT
                )
            else:
                # Just create the branch without checking it out
                result = subprocess.run(
                    ["git", "branch", branch_name],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIMEOUT
                )
            
            if result.returncode == 0:
                return True, result.stdout
            return False, result.stderr
            
        except Exception as e:
            debug_print(f"Error creating branch: {str(e)}")
            return False, str(e) 