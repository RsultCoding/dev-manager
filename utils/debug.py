import time

def debug_print(message):
    """Print debug messages with a timestamp prefix"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[DEBUG {timestamp}] {message}") 