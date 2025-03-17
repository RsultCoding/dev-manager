import os

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Change SITES_DIR to go directly to Sites folder, not parent of BASE_DIR
SITES_DIR = os.path.join(os.path.expanduser('~'), 'Sites')

# New cache file - separate from the original
CACHE_FILE = os.path.join(BASE_DIR, 'dev_support_projects.json')

# Security settings
ALLOWED_SCRIPT_DIRS = [SITES_DIR]  # Restrict script execution to these directories
SUBPROCESS_TIMEOUT = 30  # Maximum time for subprocess execution (seconds)

# Restricted commands (don't allow these in scripts)
RESTRICTED_COMMANDS = [
    "rm -rf", "sudo", "chmod", "chown", 
    "> /dev/null", "/etc/passwd", "/etc/shadow"
]

# Log file for all operations
LOG_FILE = os.path.join(BASE_DIR, 'dev_support.log')

# Enable/disable features
ENABLE_LOGGING = True
DOCKER_ENABLED = True
