# JSON Editor

The Dev-Manager application includes a built-in JSON editor that allows users to modify configuration files like `project_info.json` and `scripts.json` through an intuitive graphical interface.

## Accessing the JSON Editor

The JSON editor can be accessed directly from the Project Panel:

- **Project Information**: Click the "Edit" button next to the "Project Information:" heading to edit `project_info.json`
- **Project Scripts**: Click the "Edit" button next to the "Project Output:" heading to edit `scripts.json`

Note: The edit buttons are only enabled when a valid project is selected.

## Editor Interface

![JSON Editor Interface](images/json_editor.png)

The JSON editor interface consists of several components:

1. **File Header**: Displays the name of the file being edited
2. **Sync Checkbox**: Allows you to control whether changes are synced back to the project directory
3. **Table View**: Shows key-value pairs in a two-column table
   - Left column: Keys (fixed width of 150px)
   - Right column: Values (stretches to fill available space)
4. **Value Editor**: A dedicated text area for editing the value of the selected table row
5. **Action Buttons**:
   - Add Row: Adds a new key-value pair to the table
   - Remove Selected: Removes the selected row(s) from the table
   - Save: Saves changes to the file
   - Cancel: Discards changes and closes the editor

## Usage Guide

### Viewing and Editing Values

1. Select any row in the table to display its value in the Value Editor below
2. Edit the value in the dedicated text area for better visibility of long text
3. The table will automatically update as you type in the Value Editor

### Adding and Removing Data

1. Click "Add Row" to create a new entry with default values
2. Update the key and value as needed
3. Select any row and click "Remove Selected" to delete it

### Saving Changes

1. Click "Save" to write changes back to the JSON file
2. The editor will preserve the original JSON structure, including nesting
3. After saving, relevant parts of the UI will update to reflect the changes

### Nested JSON Structure Support

The editor supports one level of nesting in JSON files. When editing files with a single top-level key containing an object (like `scripts.json`), the editor will:

1. Detect the nested structure automatically
2. Show the contents of the nested object for editing
3. Preserve the original structure when saving

## Advanced Features

### Dual Storage System

The application maintains JSON files in two locations:

1. **Project Directory**: The original location in each project's root folder
2. **Database Directory**: A centralized database storage (`database/projects/[project-name]/`)

This dual-storage approach provides several benefits:
- Centralized management of configuration files
- Protection against accidental changes to project files
- Easy comparison between versions

### Version Management

When you edit a JSON file, the system:

1. Prioritizes the database version for editing by default
2. Automatically detects differences between project and database versions
3. Presents a dialog when differences are found, showing:
   - Which version is newer
   - Content preview of both versions
   - Options to choose which version to edit

### Difference Detection

![Differences Dialog](images/json_diff.png)

When differences are detected between project and database versions:

1. A dialog displays both versions with their content
2. Clear buttons allow you to choose which version to edit:
   - "Use Project Version": Opens the file from the project directory
   - "Use Database Version": Opens the file from the database directory
   - "Cancel": Aborts the editing operation

### Synchronization

The JSON editor includes a checkbox to control synchronization behavior:

- When checked, changes are saved to both the edited file and its counterpart
- When unchecked, changes affect only the selected version

This gives you control over whether changes propagate between project and database versions.

## Technical Details

- The JSON editor is implemented in the `JsonEditorDialog` class
- It preserves the formatting and structure of the original JSON files
- The editor handles basic validation of JSON data
- Improved UI with resizable split view between the table and value editor

The dual storage system is implemented with these components:

- **Database Directory**: `database/projects/[project-name]/`
- **Scanning**: Project JSON files are automatically copied to the database during scanning
- **Synchronization**: JSON files can be synced in both directions
- **Version Comparison**: Intelligent detection of differences based on content and modification time

When saving files:
1. Changes are always saved to the version being edited
2. If synchronization is enabled, changes are also copied to the other location
3. Future edits will detect which version is newer

## Tips and Best Practices

- Use the Value Editor for long text entries rather than trying to edit them in the table cells
- The vertical splitter between the table and Value Editor can be adjusted to give more space to either section
- Keep key names simple and descriptive
- The editor is designed for simple configuration files and not for complex nested JSON structures

## Tips for Working with Dual Storage

- Use the database version for regular editing to avoid directly modifying project files
- When collaborating, be aware that others might modify the project version
- If you intentionally want different versions, uncheck the sync option when saving
- During project scanning, newer versions are detected and synchronized automatically
