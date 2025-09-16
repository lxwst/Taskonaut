#!/usr/bin/env python3
"""
Arbeitszeit Tracker - Main Entry Point (Beautiful Clean Version)

A beautiful clean desktop overlay for time tracking with JSON database and Excel export.
"""

import tkinter as tk
import sys
import os

# Add current directory and src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))  # Add parent directory

from gui.beautiful_clean_overlay import BeautifulCleanOverlay


def main():
    """Main application entry point"""
    try:
        # Create main window (hidden)
        root = tk.Tk()
        root.title("taskonaut - Beautiful Clean")
        
        # Create application
        app = BeautifulCleanOverlay(root)
        
        # Start main loop
        print("🚀 Starting Beautiful Clean taskonaut...")
        print("📊 Using JSON database with Excel export")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)