# Dev-Manager

A PyQt6-based application for managing development projects and Docker containers.

## Features

- Project scanning and management
- Project information display
- Script execution for projects
- Docker container monitoring
- Docker image listing with table view
- Git repository management and operations
- JSON file editing with intuitive UI

## Installation

1. Ensure you have Python 3.6+ installed
2. Install dependencies: `pip install PyQt6`
3. Run the application: `python3 -m main`

## Project Structure

This project follows the MVC (Model-View-Controller) pattern:

- **Models**: Data structures and business logic
- **Views**: UI components
- **Services**: Interaction with external systems
- **Utils**: Helper functions and utilities

## Configuration

The application can be configured by editing the `config.py` file:

- Set scan directories
- Configure security settings
- Adjust timeout settings
- Enable/disable features

## JSON Editor

The application includes a built-in JSON editor for modifying configuration files:

- Edit project information and scripts with a user-friendly interface
- Table-based key-value editing with dedicated text area for long values
- Support for both simple and nested JSON structures
- **Dual storage system** that maintains copies of JSON files in both project directories and a central database
- Intelligent handling of differences between project and database versions
- See `json_editor.md` for detailed usage instructions

## Git Functionality

The application includes Git functionality for managing project repositories:

- **Status Display**: View modified, staged, and untracked files with color coding
  - Green: Staged files
  - Red: Untracked files
  - Gray: Modified but unstaged files
  
- **File Staging**: Individual file staging/unstaging using checkboxes

- **Branch Management**:
  - Current branch display at the top of the Git panel
  - Branch selection via dropdown list
  - Branch checkout capability
  - Create new branches with the "New" button
  
- **Staging Actions**:
  - Stage All: Add all modified files to staging
  - Unstage All: Remove all files from staging
  - Refresh: Update Git status information
  
- **Commit Operations**:
  - Commit message entry with multi-line support
  - Commit Only: Commit changes locally
  - Commit & Push: Commit changes and push to remote
  
- **Repository Actions**:
  - Pull: Pull latest changes from remote
  - Stash: Temporarily store modified files
  - Pop Stash: Restore stashed changes
  
- **History**: View recent commits with timestamps

- **Visual Feedback**: Status messages for all operations with automatic clearing

All Git operations are specific to the currently selected project and will update automatically when switching between projects that are Git repositories.

## Development

See `implementation.md` for detailed implementation details. 