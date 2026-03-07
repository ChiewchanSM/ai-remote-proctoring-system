import pygetwindow as gw
import time
import config

# List of words that will instantly trigger an alert if seen in the window title
FORBIDDEN_WORDS = ["chatgpt", "discord", "google", "bing", "line", "whatsapp", "messenger"]

def check_active_window():
    """Checks the currently active window and returns a violation string if cheating is detected, else None."""
    try:
        # Get the window the user is currently interacting with
        active_window = gw.getActiveWindow()
        
        if active_window is not None:
            window_title = active_window.title.lower()
            
            # Check against our blacklist
            for word in FORBIDDEN_WORDS:
                if word in window_title:
                    return f"Forbidden App Opened ({word})"
                    
    except Exception as e:
        pass
        
    return None