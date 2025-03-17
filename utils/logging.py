import os
import time
from config import LOG_FILE, ENABLE_LOGGING

def log_event(event_type, message):
    """Log an event to the log file"""
    if not ENABLE_LOGGING:
        return
        
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{event_type}] {message}\n"
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except Exception:
        # Fail silently - we don't want logging to break functionality
        pass 