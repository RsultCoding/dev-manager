# Git Functionality Implementation

This document describes the technical implementation of the Git functionality in the Dev-Manager application.

## Architecture

The Git functionality follows the application's MVC architecture:

- **Model**: The `Project` class in `models/project.py` is extended with Git-related properties and methods
- **View**: The `GitPanel` class in `views/git_panel.py` provides the UI components
- **Service**: The `GitService` class in `services/git_service.py` handles the interaction with Git

## Service Layer Implementation

The `GitService` class provides an interface to Git operations through subprocess calls:

### Repository Information
- `is_git_repo`: Checks if a directory is a Git repository
- `get_current_branch`: Gets the current branch name
- `get_status`: Gets file status (modified, staged, untracked)
- `get_branches`: Gets available branches (local and remote)
- `get_recent_commits`: Gets recent commit history

### File Operations
- `stage_file`: Stages a single file
- `unstage_file`: Unstages a single file
- `stage_all`: Stages all files
- `unstage_all`: Unstages all files

### Branch Operations
- `checkout_branch`: Switches to a branch
- `create_branch`: Creates and optionally checks out a new branch

### Repository Operations
- `commit`: Commits changes with message
- `pull`: Pulls changes from remote
- `stash`: Stashes changes
- `pop_stash`: Applies stashed changes

Each operation returns a tuple `(success, message)` to indicate success or failure and provide feedback.

## User Interface

The GitPanel UI provides several components:

- **Branch Display**: Shows current branch and provides branch switching
- **File List**: Shows modified files with checkboxes for staging/unstaging
- **Action Buttons**: Quick actions for common Git operations
- **Commit Area**: Text area for commit messages and commit buttons
- **Status Messages**: Temporary feedback for operation results

## Data Flow

1. When a project is selected in the main UI:
   - `ProjectPanel.show_project_info()` updates the Git panel
   - `GitPanel.update_for_project()` is called with the selected project
   - The GitPanel checks if the project is a Git repository
   - If it is, it enables the panel and loads Git information

2. When Git operations are performed:
   - The UI triggers a method in the GitPanel
   - The GitPanel calls the appropriate GitService method
   - Results are displayed as status messages
   - UI is refreshed to show the updated state

## Error Handling

Errors are handled at multiple levels:

- Services catch exceptions from Git commands and return error messages
- The UI displays errors to the user via QMessageBox or status messages
- Failed operations do not disrupt the application flow

## Styling and Appearance

The Git panel uses standard Qt styles with some customizations:

- Color coding for file status (green, red, gray)
- Status messages that automatically disappear after a few seconds
- Consistent button styling throughout the panel 