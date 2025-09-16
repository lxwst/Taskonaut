"""
Window utility functions for centering and positioning dialogs
"""

import tkinter as tk


def center_window(window, width: int, height: int, parent=None):
    """
    Center a window on the screen or relative to parent.
    
    Args:
        window: The tkinter window to center
        width: Desired width
        height: Desired height  
        parent: Optional parent window to center relative to
    """
    try:
        # Hide window during positioning to prevent flicker
        window.withdraw()
        
        if parent and parent.winfo_exists():
            # Center relative to parent
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            
            x = parent_x + (parent_w - width) // 2
            y = parent_y + (parent_h - height) // 2
        else:
            # Center on screen
            screen_w = window.winfo_screenwidth()
            screen_h = window.winfo_screenheight()
            x = (screen_w - width) // 2
            y = (screen_h - height) // 2
        
        # Ensure window stays on screen
        x = max(0, min(x, window.winfo_screenwidth() - width))
        y = max(0, min(y, window.winfo_screenheight() - height))
        
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set minimum size (60% of requested size)
        try:
            min_w = max(300, int(width * 0.6))
            min_h = max(200, int(height * 0.6))
            window.minsize(min_w, min_h)
        except Exception:
            pass
        
        # Show window after positioning
        window.deiconify()
        window.lift()
            
    except Exception as e:
        print(f"Error centering window: {e}")
        # Ensure window is visible even if positioning fails
        try:
            window.deiconify()
        except:
            pass
        # Fallback to default positioning
        window.geometry(f"{width}x{height}")


def get_optimal_dialog_size(content_type: str):
    """
    Get optimal dialog sizes for different content types.
    
    Args:
        content_type: Type of dialog ('session_editor', 'settings', 'note_dialog', etc.)
        
    Returns:
        Tuple of (width, height)
    """
    sizes = {
        'session_editor': (1000, 700),
        'settings': (650, 650), 
        'note_dialog': (500, 350),
        'project_editor': (450, 400),
        'simple_editor': (800, 600),
        'edit_session': (550, 550),
        'stats': (450, 480),
        'default': (500, 400)
    }
    
    return sizes.get(content_type, sizes['default'])
