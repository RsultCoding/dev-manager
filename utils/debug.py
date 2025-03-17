import time
import os

def debug_print(message):
    """Print debug messages with a timestamp prefix and log to file"""
    timestamp = time.strftime("%H:%M:%S")
    console_message = f"[DEBUG {timestamp}] {message}"
    print(console_message)
    
    # Also log to file
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "debug.log")
    
    try:
        with open(log_file, "a") as f:
            f.write(f"{console_message}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {str(e)}") 