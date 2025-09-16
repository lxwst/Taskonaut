"""
Beautiful Clean Modern Overlay - GUI Module

Modern flat design with clean buttons and pleasant interactions
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta
import threading
import time
import sys
import os
from utils.window_utils import center_window, get_optimal_dialog_size

# Import core modules
from core.json_database import JsonDatabase
from core.excel_report_manager import ExcelReportManager


class BeautifulCleanOverlay:
    """Beautiful clean modern overlay with polished buttons"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize database
        self.json_db = JsonDatabase()
        # Direct Excel report manager (replaces old ExcelExporter facade)
        self.excel_report_manager = ExcelReportManager(
            self.json_db.config_data.get('excel_file', 'working_hours.xlsx')
        )
        
        # UI state
        self.is_running = False
        self.update_thread = None
        self.update_running = False
        
        # Get active project/task
        self.current_project, self.current_task = self.json_db.get_active_project_task()
        
        # Create overlay window
        self.create_overlay()
        
        # Start update loop
        self.start_update_loop()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_beautiful_button(self, parent, text, bg_color, hover_color, command, **kwargs):
        """Create a beautiful button with hover effects"""
        btn = tk.Button(parent, text=text, bg=bg_color, fg='white',
                       font=('Segoe UI', 9, 'bold'), bd=0, cursor='hand2',
                       activebackground=hover_color, activeforeground='white',
                       relief='flat', padx=10, pady=5, command=command, **kwargs)
        
        # Add hover effects
        def on_enter(e):
            btn.configure(bg=hover_color)
        
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_overlay(self):
        """Create a minimal, borderless, compact overlay"""
        # Window setup - Load settings from config
        # Get overlay settings from config
        config = self.json_db.config_data
        overlay_settings = config.get('overlay_settings', {})
        overlay_config = config.get('overlay', {})
        
        # Use overlay_settings first, fallback to overlay, then defaults
        width = overlay_settings.get('size', '320x180').split('x')[0] if 'x' in str(overlay_settings.get('size', '320x180')) else overlay_config.get('width', 320)
        height = overlay_settings.get('size', '320x180').split('x')[1] if 'x' in str(overlay_settings.get('size', '320x180')) else overlay_config.get('height', 180)
        pos_x = overlay_settings.get('position', {}).get('x', overlay_config.get('position', {}).get('x', 100))
        pos_y = overlay_settings.get('position', {}).get('y', overlay_config.get('position', {}).get('y', 100))
        alpha = overlay_settings.get('alpha', overlay_config.get('transparency', 0.92))
        topmost = overlay_settings.get('topmost', True)
        
        # Configure window with settings from config
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.root.attributes('-topmost', topmost)
        self.root.attributes('-alpha', alpha)
        self.root.resizable(False, False)
        self.root.configure(bg='#ffffff')
        
        # Remove window decorations for clean look
        self.root.overrideredirect(True)
        
        # Main container with subtle shadow
        main_frame = tk.Frame(self.root, bg='#ffffff', bd=1, relief='solid', 
                             highlightbackground='#e0e0e0', highlightthickness=1)
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Draggable header area (minimal)
        self.header = tk.Frame(main_frame, bg='#f8f9fa', height=25, cursor='hand2')
        self.header.pack(fill='x')
        self.header.pack_propagate(False)
        
        # Compact title
        title_frame = tk.Frame(self.header, bg='#f8f9fa')
        title_frame.pack(fill='both', expand=True, padx=8, pady=3)
        
        title_label = tk.Label(title_frame, text="⏱️ Tracker", 
                              bg='#f8f9fa', fg='#2c3e50',
                              font=('Segoe UI', 10, 'bold'), cursor='hand2')
        title_label.pack(side='left')
        
        # CLOSE button in header (top right)
        self.close_btn = tk.Button(title_frame,
                                  text="❌",
                                  bg='#e74c3c', fg='white',
                                  font=('Segoe UI', 8),
                                  width=2, height=1,
                                  bd=0, relief='flat',
                                  cursor='hand2',
                                  command=self.on_closing)
        self.close_btn.pack(side='right')
        
        # Make header draggable
        self.make_draggable(self.header)
        self.make_draggable(title_label)
        
        # Auto-save position when window is moved
        self.root.bind('<Configure>', self.on_window_configure)
        
        # Content area
        content = tk.Frame(main_frame, bg='#ffffff')
        content.pack(fill='both', expand=True, padx=8, pady=5)
        
        # Time displays area - Arbeitszeit (grün), Pausenzeit (orange), Übrige Zeit (schwarz)
        time_display_frame = tk.Frame(content, bg='#ffffff')
        time_display_frame.pack(fill='x', pady=(0, 8))
        
        # Arbeitszeit (grün)
        work_time_frame = tk.Frame(time_display_frame, bg='#ffffff')
        work_time_frame.pack(side='left', padx=(0, 12))
        
        self.work_time_label = tk.Label(work_time_frame, text="0h 00m",
                                       bg='#ffffff', fg='#27ae60',
                                       font=('Segoe UI', 11, 'bold'))
        self.work_time_label.pack()
        
        # Pausenzeit (orange) 
        break_time_frame = tk.Frame(time_display_frame, bg='#ffffff')
        break_time_frame.pack(side='left', padx=(0, 12))
        
        self.break_time_label = tk.Label(break_time_frame, text="0h 00m",
                                        bg='#ffffff', fg='#f39c12',
                                        font=('Segoe UI', 11, 'bold'))
        self.break_time_label.pack()
        
        # Übrige Arbeitszeit (schwarz)
        remaining_time_frame = tk.Frame(time_display_frame, bg='#ffffff')
        remaining_time_frame.pack(side='left')
        
        self.remaining_time_label = tk.Label(remaining_time_frame, text="8h 00m",
                                            bg='#ffffff', fg='#2c3e50',
                                            font=('Segoe UI', 11, 'bold'))
        self.remaining_time_label.pack()
        
        # Current session timer (violet) - upper right
        current_session_frame = tk.Frame(time_display_frame, bg='#ffffff')
        current_session_frame.pack(side='right')
        
        self.current_session_label = tk.Label(current_session_frame, text="0h 00m",
                                             bg='#ffffff', fg="#d3585e",
                                             font=('Segoe UI', 11, 'bold'))
        self.current_session_label.pack()
        
        # Project/Task display area (clickable)
        project_display_frame = tk.Frame(content, bg='#f8f9fa', relief='solid', bd=1, cursor='hand2')
        project_display_frame.pack(fill='x', pady=(0, 8))
        
        # Project text (larger, clickable)
        project_text = f"{self.current_project} | {self.current_task}"
        if len(project_text) > 35:
            project_text = project_text[:32] + "..."
        
        self.project_display_label = tk.Label(project_display_frame, text=project_text,
                                             bg='#f8f9fa', fg='#2c3e50',
                                             font=('Segoe UI', 11, 'bold'), 
                                             cursor='hand2', anchor='center')
        self.project_display_label.pack(fill='x', padx=8, pady=6)
        
        # Bind click events for project/task editing
        self.project_display_label.bind('<Button-1>', self.show_project_task_editor)  # Left click = Edit dialog
        self.project_display_label.bind('<Button-3>', self.show_project_switch_menu)  # Right click = Quick switch
        project_display_frame.bind('<Button-1>', self.show_project_task_editor)
        project_display_frame.bind('<Button-3>', self.show_project_switch_menu)
        
        # Compact button area
        button_frame = tk.Frame(content, bg='#ffffff')
        button_frame.pack(fill='x')
        
        # START/PAUSE button (extra compact)
        self.play_btn = tk.Button(button_frame,
                                 text="▶",
                                 bg='#27ae60', fg='white',
                                 font=('Segoe UI', 9, 'bold'),
                                 width=3, height=1,
                                 bd=0, relief='flat',
                                 cursor='hand2',
                                 command=self.toggle_play_pause)
        self.play_btn.pack(side='left', padx=(0, 2))
        
        # STATS button (extra compact)
        self.stats_btn = tk.Button(button_frame,
                                  text="📊",
                                  bg='#3498db', fg='white',
                                  font=('Segoe UI', 8),
                                  width=3, height=1,
                                  bd=0, relief='flat',
                                  cursor='hand2',
                                  command=self.show_stats)
        self.stats_btn.pack(side='right', padx=(2, 0))
        
        # SESSION EDITOR button (extra compact)
        self.session_editor_btn = tk.Button(button_frame,
                                          text="📝",
                                          bg='#9b59b6', fg='white',
                                          font=('Segoe UI', 8),
                                          width=3, height=1,
                                          bd=0, relief='flat',
                                          cursor='hand2',
                                          command=self.show_session_editor)
        self.session_editor_btn.pack(side='right', padx=(2, 0))
        
        # SETTINGS button (extra compact)
        self.settings_btn = tk.Button(button_frame,
                                     text="⚙",
                                     bg='#95a5a6', fg='white',
                                     font=('Segoe UI', 8),
                                     width=3, height=1,
                                     bd=0, relief='flat',
                                     cursor='hand2',
                                     command=self.show_settings)
        self.settings_btn.pack(side='right')
        
        # Add hover effects
        self.setup_compact_hover_effects()
        
        # Update display
        self.update_display()
        
        print("✨ Minimal borderless overlay created!")
    
    def setup_compact_hover_effects(self):
        """Setup compact button hover effects"""
        # Play button hover effects
        def on_play_enter(e):
            current_text = self.play_btn.cget('text')
            if current_text == "▶":
                self.play_btn.configure(bg='#229954')  # Darker green
            else:  # ⏸
                self.play_btn.configure(bg='#d68910')  # Darker orange
        
        def on_play_leave(e):
            current_text = self.play_btn.cget('text')
            if current_text == "▶":
                self.play_btn.configure(bg='#27ae60')  # Original green
            else:  # ⏸
                self.play_btn.configure(bg='#f39c12')  # Original orange
        
        self.play_btn.bind('<Enter>', on_play_enter)
        self.play_btn.bind('<Leave>', on_play_leave)
        
        # Other button hover effects
        self.stats_btn.bind('<Enter>', lambda e: self.stats_btn.configure(bg='#2980b9'))
        self.stats_btn.bind('<Leave>', lambda e: self.stats_btn.configure(bg='#3498db'))
        
        # Session Editor button hover effects
        self.session_editor_btn.bind('<Enter>', lambda e: self.session_editor_btn.configure(bg='#8e44ad'))
        self.session_editor_btn.bind('<Leave>', lambda e: self.session_editor_btn.configure(bg='#9b59b6'))
        
        self.settings_btn.bind('<Enter>', lambda e: self.settings_btn.configure(bg='#7f8c8d'))
        self.settings_btn.bind('<Leave>', lambda e: self.settings_btn.configure(bg='#95a5a6'))
        
        # Close button hover effects
        self.close_btn.bind('<Enter>', lambda e: self.close_btn.configure(bg='#c0392b'))
        self.close_btn.bind('<Leave>', lambda e: self.close_btn.configure(bg='#e74c3c'))
    
    def update_current_project_task(self, event=None):
        """Update current project and task (simplified - no longer uses comboboxes)"""
        # This method is kept for backwards compatibility but is no longer used
        # Project/Task changes now happen through the dedicated editor dialogs
        pass
    
    def show_recent_projects(self, event=None):
        """Show context menu with recent projects"""
        try:
            # Get unique projects from recent sessions
            recent_projects = set()
            for session in self.json_db.sessions[-20:]:  # Last 20 sessions
                if session.project and session.project != 'BREAK':
                    recent_projects.add(session.project)
            
            if not recent_projects:
                return
            
            # Create context menu
            menu = tk.Menu(self.root, tearoff=0)
            for project in sorted(recent_projects)[:10]:  # Show max 10
                menu.add_command(label=project, 
                               command=lambda p=project: self.set_project(p))
            
            # Show menu at mouse position
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
                
        except Exception as e:
            print(f"Error showing recent projects: {e}")
    
    def show_recent_tasks(self, event=None):
        """Show context menu with recent tasks"""
        try:
            # Get unique tasks from recent sessions with current project
            recent_tasks = set()
            current_proj = self.project_var.get() or self.current_project
            
            for session in self.json_db.sessions[-30:]:  # Last 30 sessions
                if session.project == current_proj and session.task:
                    recent_tasks.add(session.task)
            
            if not recent_tasks:
                # Fallback: show all recent tasks
                for session in self.json_db.sessions[-20:]:
                    if session.task and session.task != 'BREAK':
                        recent_tasks.add(session.task)
            
            if not recent_tasks:
                return
            
            # Create context menu
            menu = tk.Menu(self.root, tearoff=0)
            for task in sorted(recent_tasks)[:10]:  # Show max 10
                menu.add_command(label=task,
                               command=lambda t=task: self.set_task(t))
            
            # Show menu at mouse position
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
                
        except Exception as e:
            print(f"Error showing recent tasks: {e}")
    
    def set_project(self, project):
        """Set project from context menu selection"""
        self.project_var.set(project)
        self.update_current_project_task()
    
    def set_task(self, task):
        """Set task from context menu selection"""
        self.task_var.set(task)
        self.update_current_project_task()
    
    def make_draggable(self, widget):
        """Make widget draggable"""
        def start_drag(event):
            widget.start_x = event.x
            widget.start_y = event.y
        
        def drag(event):
            x = self.root.winfo_x() + (event.x - widget.start_x)
            y = self.root.winfo_y() + (event.y - widget.start_y)
            self.root.geometry(f"+{x}+{y}")
        
        widget.bind('<Button-1>', start_drag)
        widget.bind('<B1-Motion>', drag)
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        active_session = self.json_db.get_active_session()
        
        if active_session is None:
            self.start_session()
        else:
            self.pause_session()
    
    def start_session(self):
        """Start new session"""
        try:
            # Stop any existing session
            self.json_db.stop_active_session()
            
            # Determine session type based on project
            session_type = 'break' if self.current_project == 'BREAK' else 'work'
            
            # Create new session with correct type
            session = self.json_db.create_session(self.current_project, self.current_task, session_type)
            
            # Update UI
            self.is_running = True
            if session_type == 'break':
                self.play_btn.configure(text="⏸", bg='#f39c12')  # Orange for breaks
                print(f"☕ Started break: {self.current_project} - {self.current_task}")
            else:
                self.play_btn.configure(text="⏸", bg='#f39c12')
                print(f"▶️ Started: {self.current_project} - {self.current_task}")
            
            # Save to JSON
            self.json_db.save_sessions()
            
        except Exception as e:
            print(f"Error starting session: {e}")
            messagebox.showerror("Error", f"Failed to start session: {e}")
    
    def pause_session(self):
        """Pause current session"""
        try:
            stopped_session = self.json_db.stop_active_session()
            
            if stopped_session:
                # Update UI
                self.is_running = False
                self.play_btn.configure(text="▶", bg='#27ae60')
                
                # Save to JSON
                self.json_db.save_sessions()
                
                duration = self.json_db.format_seconds(stopped_session.duration_seconds)
                print(f"⏸️ Paused: {stopped_session.project} - {stopped_session.task} ({duration})")
            
        except Exception as e:
            print(f"Error pausing session: {e}")
            messagebox.showerror("Error", f"Failed to pause session: {e}")
    
    def show_stats(self):
        """Show beautiful statistics window"""
        # Calculate today's stats
        work_seconds = self.json_db.get_today_work_seconds()
        break_seconds = self.json_db.get_today_break_seconds()
        
        work_time = self.json_db.format_seconds(work_seconds)
        break_time = self.json_db.format_seconds(break_seconds)
        
        # Calculate work day start and end times
        today_sessions = self.json_db.get_today_sessions('work')
        work_day_start = None
        work_day_end = None
        
        if today_sessions:
            # Find earliest start time (work day start)
            work_day_start = min(session.start_time for session in today_sessions)
            
            # Calculate required work end time
            required_work_seconds = self.json_db.get_today_required_work_seconds()
            total_break_seconds = break_seconds
            
            # End time = start + required_work + break_time
            from datetime import timedelta
            total_duration = timedelta(seconds=required_work_seconds + total_break_seconds)
            work_day_end = work_day_start + total_duration
        
    # Create beautiful stats window (larger to fit new info)
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Today's Statistics")
        stats_window.configure(bg='#ffffff')
        stats_window.resizable(False, False)
        stats_window.transient(self.root)
        center_window(stats_window, 400, 420)  # Center after configuration
        # stats_window.overrideredirect(True)  # Disabled for visibility
        
        # Add border to stats window
        stats_container = tk.Frame(stats_window, bg='#ffffff', bd=1, relief='solid')
        stats_container.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(stats_container, bg='#f8f9fa', height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Today's Statistics", 
                bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Content
        content = tk.Frame(stats_container, bg='#ffffff')
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Work day start time
        if work_day_start:
            start_frame = tk.Frame(content, bg='#ffffff')
            start_frame.pack(fill='x', pady=12)
            
            tk.Label(start_frame, text="🌅", bg='#ffffff', 
                    font=('Segoe UI', 18)).pack(side='left', padx=(0, 10))
            
            start_time_str = work_day_start.strftime('%H:%M')
            tk.Label(start_frame, text=f"Work Day Start: {start_time_str}",
                    bg='#ffffff', fg='#3498db', 
                    font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        # Stats with icons and colors
        work_frame = tk.Frame(content, bg='#ffffff')
        work_frame.pack(fill='x', pady=12)
        
        tk.Label(work_frame, text="⏱️", bg='#ffffff', 
                font=('Segoe UI', 18)).pack(side='left', padx=(0, 10))
        
        tk.Label(work_frame, text=f"Work Time: {work_time}",
                bg='#ffffff', fg='#27ae60', 
                font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        break_frame = tk.Frame(content, bg='#ffffff')
        break_frame.pack(fill='x', pady=12)
        
        tk.Label(break_frame, text="☕", bg='#ffffff', 
                font=('Segoe UI', 18)).pack(side='left', padx=(0, 10))
        
        tk.Label(break_frame, text=f"Break Time: {break_time}",
                bg='#ffffff', fg='#f39c12', 
                font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        # Work day end time (calculated)
        if work_day_end:
            end_frame = tk.Frame(content, bg='#ffffff')
            end_frame.pack(fill='x', pady=12)
            
            tk.Label(end_frame, text="🌇", bg='#ffffff', 
                    font=('Segoe UI', 18)).pack(side='left', padx=(0, 10))
            
            end_time_str = work_day_end.strftime('%H:%M')
            tk.Label(end_frame, text=f"Work Day end: {end_time_str}",
                    bg='#ffffff', fg='#e74c3c', 
                    font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        # Export button
        button_frame = tk.Frame(content, bg='#ffffff')
        button_frame.pack(fill='x', pady=25)
        
        export_btn = tk.Button(button_frame, text="📊 Export to Excel",
                              bg='#3498db', fg='white', 
                              font=('Segoe UI', 10, 'bold'),
                              width=20, height=2, bd=0, cursor='hand2',
                              command=lambda: self.export_and_close_stats(stats_window))
        export_btn.pack()
        
        # Add hover effect to export button
        export_btn.bind('<Enter>', lambda e: export_btn.configure(bg='#2980b9'))
        export_btn.bind('<Leave>', lambda e: export_btn.configure(bg='#3498db'))
        
        print("📊 Beautiful borderless stats window opened")
    
    def make_draggable_window(self, widget, window):
        """Make a window draggable"""
        def start_drag(event):
            widget.start_x = event.x
            widget.start_y = event.y
        
        def drag(event):
            x = window.winfo_x() + (event.x - widget.start_x)
            y = window.winfo_y() + (event.y - widget.start_y)
            window.geometry(f"+{x}+{y}")
        
        widget.bind('<Button-1>', start_drag)
        widget.bind('<B1-Motion>', drag)

    def center_window(self, window, width: int, height: int):
        """Center a given window using the centralized window_utils function."""
        from utils.window_utils import center_window as center_window_util
        center_window_util(window, width, height, parent=self.root)
    
    def export_and_close_stats(self, window):
        """Export data with user choice and close stats window"""
        try:
            # Ask user what to export
            result = messagebox.askyesnocancel("Export Options", 
                                             "Export ALL sessions?\n\n"
                                             "• Yes = Export all sessions from all days\n"
                                             "• No = Export only today's sessions\n"
                                             "• Cancel = Don't export")
            
            if result is None:  # Cancel
                return
            elif result:  # Yes - Export all
                if self.excel_report_manager.export_all(self.json_db):
                    messagebox.showinfo("Success", f"All sessions exported to {self.excel_report_manager.excel_file}")
                else:
                    messagebox.showerror("Error", "Failed to export all data")
            else:  # No - Export today only
                if self.excel_report_manager.export_all(self.json_db):  # Today-only deprecated -> full export
                    messagebox.showinfo("Success", f"Today's data exported to {self.excel_report_manager.excel_file}")
                else:
                    messagebox.showerror("Error", "Failed to export today's data")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
        finally:
            window.destroy()
    
    def show_settings(self):
        """Show complete settings window with all configuration options"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙ Settings & Configuration")
        settings_window.configure(bg='#ffffff')
        settings_window.resizable(True, True)
        settings_window.transient(self.root)
        center_window(settings_window, 750, 900)  # Larger window size for better layout
        
        # Create notebook for tabs
        notebook = tk.Frame(settings_window, bg='#ffffff')
        notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Get current config values
        config = self.json_db.config_data
        overlay_settings = config.get('overlay_settings', {})
        overlay_config = config.get('overlay', {})
        
        # Overlay Configuration Section
        overlay_frame = tk.LabelFrame(notebook, text="🖥️ Overlay Configuration", 
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#ffffff', fg='#2c3e50', padx=10, pady=10)
        overlay_frame.pack(fill='x', pady=(0, 15))
        
        # Window size settings (load from config)
        size_frame = tk.Frame(overlay_frame, bg='#ffffff')
        size_frame.pack(fill='x', pady=5)
        
        tk.Label(size_frame, text="Window Size:", bg='#ffffff', 
                font=('Segoe UI', 10)).pack(side='left')
        
        # Get current size from config or use default
        current_size = overlay_settings.get('size', f"{overlay_config.get('width', 320)}x{overlay_config.get('height', 180)}")
        size_var = tk.StringVar(value=current_size)
        size_combo = tk.Entry(size_frame, textvariable=size_var, width=15)
        size_combo.pack(side='right')
        
        # Transparency settings (load from config)
        alpha_frame = tk.Frame(overlay_frame, bg='#ffffff')
        alpha_frame.pack(fill='x', pady=5)
        
        tk.Label(alpha_frame, text="Transparency:", bg='#ffffff',
                font=('Segoe UI', 10)).pack(side='left')
        
        # Get current alpha from config or use default
        current_alpha = overlay_settings.get('alpha', overlay_config.get('transparency', 0.92))
        alpha_var = tk.DoubleVar(value=current_alpha)
        alpha_scale = tk.Scale(alpha_frame, from_=0.5, to=1.0, resolution=0.05,
                              orient='horizontal', variable=alpha_var, bg='#ffffff')
        alpha_scale.pack(side='right')
        
        # Always on top (load from config)
        current_topmost = overlay_settings.get('topmost', True)
        topmost_var = tk.BooleanVar(value=current_topmost)
        topmost_check = tk.Checkbutton(overlay_frame, text="Always stay on top",
                                      variable=topmost_var, bg='#ffffff',
                                      font=('Segoe UI', 10))
        topmost_check.pack(anchor='w', pady=5)
        
        # Project & Task Configuration
        project_frame = tk.LabelFrame(notebook, text="📋 Project & Task Settings",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#ffffff', fg='#2c3e50', padx=10, pady=10)
        project_frame.pack(fill='x', pady=(0, 15))
        
        # Current project selection
        proj_frame = tk.Frame(project_frame, bg='#ffffff')
        proj_frame.pack(fill='x', pady=5)
        
        tk.Label(proj_frame, text="Current Project:", bg='#ffffff',
                font=('Segoe UI', 10)).pack(side='left')
        
        project_var = tk.StringVar(value=self.current_project)
        project_entry = tk.Entry(proj_frame, textvariable=project_var, width=20)
        project_entry.pack(side='right')
        
        # Current task selection
        task_frame = tk.Frame(project_frame, bg='#ffffff')
        task_frame.pack(fill='x', pady=5)
        
        tk.Label(task_frame, text="Current Task:", bg='#ffffff',
                font=('Segoe UI', 10)).pack(side='left')
        
        task_var = tk.StringVar(value=self.current_task)
        task_entry = tk.Entry(task_frame, textvariable=task_var, width=20)
        task_entry.pack(side='right')
        
        # Task Management Section
        task_mgmt_frame = tk.LabelFrame(notebook, text="📝 Task Management",
                                       font=('Segoe UI', 11, 'bold'),
                                       bg='#ffffff', fg='#2c3e50', padx=10, pady=10)
        task_mgmt_frame.pack(fill='x', pady=(0, 15))
        
        # Project selection for task management
        proj_mgmt_frame = tk.Frame(task_mgmt_frame, bg='#ffffff')
        proj_mgmt_frame.pack(fill='x', pady=5)
        
        tk.Label(proj_mgmt_frame, text="Manage Project:", bg='#ffffff',
                font=('Segoe UI', 10)).pack(side='left')
        
        mgmt_project_var = tk.StringVar(value=self.current_project)
        mgmt_project_combo = ttk.Combobox(proj_mgmt_frame, textvariable=mgmt_project_var,
                                         values=self.json_db.get_available_projects(),
                                         width=18, state='readonly')
        mgmt_project_combo.pack(side='right')
        
        # Task list and management
        tasks_frame = tk.Frame(task_mgmt_frame, bg='#ffffff')
        tasks_frame.pack(fill='both', expand=True, pady=10)
        
        # Left side: Current tasks
        current_tasks_frame = tk.Frame(tasks_frame, bg='#ffffff')
        current_tasks_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(current_tasks_frame, text="Current Tasks:", bg='#ffffff',
                font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        
        # Listbox for current tasks
        self.task_listbox = tk.Listbox(current_tasks_frame, height=4, 
                                      font=('Segoe UI', 9))
        self.task_listbox.pack(fill='both', expand=True, pady=5)
        
        # Right side: Add/Remove tasks
        task_actions_frame = tk.Frame(tasks_frame, bg='#ffffff')
        task_actions_frame.pack(side='right')
        
        # Add new task
        add_task_frame = tk.Frame(task_actions_frame, bg='#ffffff')
        add_task_frame.pack(pady=5)
        
        tk.Label(add_task_frame, text="New Task:", bg='#ffffff',
                font=('Segoe UI', 9)).pack()
        
        self.new_task_var = tk.StringVar()
        new_task_entry = tk.Entry(add_task_frame, textvariable=self.new_task_var, width=15)
        new_task_entry.pack(pady=2)
        
        def add_task():
            project = mgmt_project_var.get()
            new_task = self.new_task_var.get().strip()
            if project and new_task:
                if self.json_db.add_task_to_project(project, new_task):
                    self.new_task_var.set("")
                    update_task_list()
                    # Update comboboxes in main window
                    if hasattr(self, 'task_combo'):
                        if self.project_var.get() == project:
                            self.task_combo['values'] = self.json_db.get_tasks_for_project(project)
        
        tk.Button(add_task_frame, text="➕ Add", bg='#27ae60', fg='white',
                 font=('Segoe UI', 8, 'bold'), command=add_task).pack(pady=2)
        
        # Remove task
        def remove_task():
            selection = self.task_listbox.curselection()
            if selection:
                project = mgmt_project_var.get()
                task_to_remove = self.task_listbox.get(selection[0])
                if project and task_to_remove:
                    # Remove from database
                    if ('projects' in self.json_db.projects_data and 
                        project in self.json_db.projects_data['projects']):
                        try:
                            self.json_db.projects_data['projects'][project].remove(task_to_remove)
                            self.json_db.save_projects()
                            update_task_list()
                            # Update comboboxes in main window
                            if hasattr(self, 'task_combo'):
                                if self.project_var.get() == project:
                                    self.task_combo['values'] = self.json_db.get_tasks_for_project(project)
                            print(f"🗑️ Removed task '{task_to_remove}' from project '{project}'")
                        except ValueError:
                            pass
        
        tk.Button(task_actions_frame, text="🗑️ Remove", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 8, 'bold'), command=remove_task).pack(pady=10)
        
        # Update task list function
        def update_task_list():
            project = mgmt_project_var.get()
            self.task_listbox.delete(0, tk.END)
            if project:
                tasks = self.json_db.get_tasks_for_project(project)
                for task in tasks:
                    self.task_listbox.insert(tk.END, task)
        
        # Bind project selection change
        mgmt_project_combo.bind('<<ComboboxSelected>>', lambda e: update_task_list())
        
        # Initial task list update
        update_task_list()
        
        # Export Settings
        export_frame = tk.LabelFrame(notebook, text="📊 Export Settings",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg='#ffffff', fg='#2c3e50', padx=10, pady=10)
        export_frame.pack(fill='x', pady=(0, 15))
        
        # Auto-export option (load from config)
        excel_config = config.get('excel_export', {})
        current_auto_export = excel_config.get('auto_export_daily', False)
        auto_export_var = tk.BooleanVar(value=current_auto_export)
        auto_export_check = tk.Checkbutton(export_frame, text="Auto-export on session end",
                                          variable=auto_export_var, bg='#ffffff',
                                          font=('Segoe UI', 10))
        auto_export_check.pack(anchor='w', pady=5)
        
        # Excel filename (load from config)
        current_excel_filename = excel_config.get('filename', config.get('excel_file', 'working_hours.xlsx'))
        excel_frame = tk.Frame(export_frame, bg='#ffffff')
        excel_frame.pack(fill='x', pady=5)
        
        tk.Label(excel_frame, text="Excel Filename:", bg='#ffffff',
                font=('Segoe UI', 10)).pack(side='left')
        
        excel_var = tk.StringVar(value=current_excel_filename)
        excel_entry = tk.Entry(excel_frame, textvariable=excel_var, width=25)
        excel_entry.pack(side='right')
        
        # Session Settings
        session_frame = tk.LabelFrame(notebook, text="⏰ Session Settings",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#ffffff', fg='#2c3e50', padx=10, pady=10)
        session_frame.pack(fill='x', pady=(0, 15))
        
        # Auto-split minutes setting
        auto_split_frame = tk.Frame(session_frame, bg='#ffffff')
        auto_split_frame.pack(fill='x', pady=5)
        
        tk.Label(auto_split_frame, text="Auto-split threshold (minutes):", bg='#ffffff',
                font=('Segoe UI', 10)).pack(side='left')
        
        # Get current auto-split setting from config
        current_auto_split = config.get('auto_split_minutes', 5)
        auto_split_var = tk.IntVar(value=current_auto_split)
        auto_split_spinbox = tk.Spinbox(auto_split_frame, from_=0, to=60, 
                                       textvariable=auto_split_var, width=10,
                                       font=('Segoe UI', 10))
        auto_split_spinbox.pack(side='right')
        
        # Help text for auto-split
        help_frame = tk.Frame(session_frame, bg='#ffffff')
        help_frame.pack(fill='x', pady=(0, 10))
        
        help_text = tk.Label(help_frame, 
                            text="💡 When switching projects via right-click, sessions ≥ threshold will auto-split",
                            bg='#ffffff', fg='#7f8c8d', font=('Segoe UI', 8),
                            wraplength=400, justify='left')
        help_text.pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(notebook, bg='#ffffff')
        button_frame.pack(fill='x', pady=15)
        
        # Apply button
        apply_btn = tk.Button(button_frame, text="✅ Apply Changes",
                             bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                             width=15, command=lambda: self.apply_settings(
                                 size_var.get(), alpha_var.get(), topmost_var.get(),
                                 project_var.get(), task_var.get(), 
                                 auto_export_var.get(), excel_var.get(), 
                                 auto_split_var.get(), settings_window))
        apply_btn.pack(side='left', padx=(0, 10))
        
        # Session Editor button
        editor_btn = tk.Button(button_frame, text="📝 Edit Sessions",
                              bg='#3498db', fg='white', font=('Segoe UI', 10, 'bold'),
                              width=15, command=self.show_session_editor)
        editor_btn.pack(side='left', padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(button_frame, text="❌ Close",
                             bg='#95a5a6', fg='white', font=('Segoe UI', 10, 'bold'),
                             width=10, command=settings_window.destroy)
        close_btn.pack(side='right')
        
        print("⚙️ Complete settings window opened")
    
    def apply_settings(self, size, alpha, topmost, project, task, auto_export, excel_filename, auto_split_minutes, window):
        """Apply settings changes"""
        try:            
            # Get current position before applying changes
            current_geometry = self.root.geometry()
            if '+' in current_geometry:
                # Extract current position
                size_part, pos_part = current_geometry.split('+', 1)
                if '+' in pos_part:
                    pos_x, pos_y = pos_part.split('+', 1)
                else:
                    pos_x, pos_y = pos_part.split('-', 1) if '-' in pos_part else ('100', '100')
            else:
                pos_x, pos_y = '100', '100'
            
            # Update window properties keeping current position
            self.root.geometry(f"{size}+{pos_x}+{pos_y}")
            self.root.attributes('-alpha', alpha)
            self.root.attributes('-topmost', topmost)
            
            # Update project and task
            self.current_project = project
            self.current_task = task
            
            # Update display
            project_text = f"{project} | {task}"
            if len(project_text) > 35:
                project_text = project_text[:32] + "..."
            self.project_display_label.configure(text=project_text)
            
            # Save to JSON config with both overlay sections
            config = self.json_db.config_data
            
            # Update overlay_settings section (keep current position)
            if 'overlay_settings' not in config:
                config['overlay_settings'] = {}
            config['overlay_settings'].update({
                'size': size,
                'alpha': alpha,
                'topmost': topmost,
                'position': {'x': int(pos_x), 'y': int(pos_y)}
            })
            
            # Also update overlay section for compatibility
            if 'overlay' not in config:
                config['overlay'] = {}
            width, height = size.split('x') if 'x' in size else ('320', '180')
            config['overlay'].update({
                'width': int(width),
                'height': int(height),
                'transparency': alpha,
                'position': {'x': int(pos_x), 'y': int(pos_y)}
            })
            
            # Update export settings
            if 'excel_export' not in config:
                config['excel_export'] = {}
            config['excel_export'].update({
                'filename': excel_filename,
                'auto_export_daily': auto_export
            })
            
            # Update session settings
            config['auto_split_minutes'] = auto_split_minutes
            
            # Also update legacy excel_file field for compatibility
            config['excel_file'] = excel_filename
            
            config['current_project'] = project
            config['current_task'] = task
            self.json_db.save_config()
            
            messagebox.showinfo("Success", f"Settings applied successfully!\n\nAuto-split threshold: {auto_split_minutes} minutes")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
            print(f"Settings apply error: {e}")
    
    def show_session_editor(self):
        """Show the full-featured session editor window"""
        try:
            from gui.session_editor import SessionEditor
            
            # Create and show the SessionEditor with JsonDatabase directly
            editor = SessionEditor(self.root, self.json_db, callback=self.update_display)
            editor.show_session_editor()
            
            print("📝 Full-featured session editor opened with JsonDatabase integration")
            
        except Exception as e:
            print(f"❌ Error opening session editor: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple editor if there's an error
            self.show_simple_session_editor()
    
    def show_project_task_editor(self, event=None):
        """Show project/task editor dialog (Left click)"""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("📝 Projekt/Task Editor")
        editor_window.configure(bg='#ffffff')
        editor_window.resizable(False, False)
        editor_window.transient(self.root)
        editor_window.grab_set()
        center_window(editor_window, 420, 380)  # Center after configuration
        
        # Header
        header_frame = tk.Frame(editor_window, bg='#f8f9fa', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📋 Projekt & Task bearbeiten", 
                bg='#f8f9fa', fg='#2c3e50',
                font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        # Content
        content_frame = tk.Frame(editor_window, bg='#ffffff')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Project selection
        tk.Label(content_frame, text="Projekt:", 
                bg='#ffffff', fg='#2c3e50',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        project_var = tk.StringVar(value=self.current_project)
        project_combo = ttk.Combobox(content_frame, textvariable=project_var,
                                    font=('Segoe UI', 10), width=35, height=8)
        project_combo['values'] = self.json_db.get_available_projects()
        project_combo.pack(fill='x', pady=(0, 15))
        
        # Task selection
        tk.Label(content_frame, text="Task:", 
                bg='#ffffff', fg='#2c3e50',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        task_var = tk.StringVar(value=self.current_task)
        task_combo = ttk.Combobox(content_frame, textvariable=task_var,
                                 font=('Segoe UI', 10), width=35, height=8)
        
        # Update task combo when project changes
        def update_tasks(event=None):
            selected_project = project_var.get()
            if selected_project:
                tasks = self.json_db.get_tasks_for_project(selected_project)
                task_combo['values'] = tasks
                if tasks and task_var.get() not in tasks:
                    task_var.set(tasks[0])
        
        project_combo.bind('<<ComboboxSelected>>', update_tasks)
        update_tasks()  # Initial update
        
        task_combo.pack(fill='x', pady=(0, 15))
        
        # Notes section
        tk.Label(content_frame, text="Notizen:", 
                bg='#ffffff', fg='#2c3e50',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Get current session note if active
        current_note = ""
        active_session = self.json_db.get_active_session()
        if active_session and hasattr(active_session, 'note'):
            current_note = active_session.note or ""
        
        notes_text = tk.Text(content_frame, height=6, width=40, 
                           font=('Segoe UI', 9), wrap='word',
                           bg='#f8f9fa', relief='solid', bd=1)
        notes_text.pack(fill='both', expand=True, pady=(0, 15))
        notes_text.insert('1.0', current_note)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ffffff')
        button_frame.pack(fill='x')
        
        def save_changes():
            try:
                new_project = project_var.get().strip()
                new_task = task_var.get().strip()
                new_notes = notes_text.get('1.0', tk.END).strip()
                
                if not new_project or not new_task:
                    messagebox.showerror("Fehler", "Projekt und Task sind erforderlich!")
                    return
                
                # Add new project/task if needed
                if new_project not in self.json_db.get_available_projects():
                    self.json_db.add_new_project(new_project, [new_task])
                elif new_task not in self.json_db.get_tasks_for_project(new_project):
                    self.json_db.add_task_to_project(new_project, new_task)
                
                # Update current project/task
                self.current_project = new_project
                self.current_task = new_task
                self.json_db.set_active_project_task(new_project, new_task)
                
                # Update active session note if exists
                active_session = self.json_db.get_active_session()
                if active_session:
                    active_session.note = new_notes
                    active_session.project = new_project
                    active_session.task = new_task
                
                # Update display
                self.update_project_display()
                
                editor_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
        
        save_btn = tk.Button(button_frame, text="💾 Speichern", 
                            bg='#27ae60', fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            command=save_changes, cursor='hand2')
        save_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="❌ Abbrechen", 
                              bg='#95a5a6', fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              command=editor_window.destroy, cursor='hand2')
        cancel_btn.pack(side='right')
    
    def show_project_switch_menu(self, event=None):
        """Show quick project switch menu (Right click)"""
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 9))
        
        # Get recent combinations from database
        recent_combinations = self.json_db.get_recent_combinations()
        
        # Add recent combinations as options
        for combination in recent_combinations[:10]:  # Limit to 10 most recent
            try:
                # Parse "Project - Task" format
                if ' - ' in combination:
                    project, task = combination.split(' - ', 1)
                else:
                    # Fallback for malformed combinations
                    project = combination
                    task = "Daily Work"
                
                # Highlight current project-task combination
                current_combination = f"{self.current_project} - {self.current_task}"
                if combination == current_combination:
                    menu.add_command(label=f"✓ {combination}", 
                                   state='disabled')
                else:
                    menu.add_command(label=f"   {combination}",
                                   command=lambda p=project, t=task: self.quick_switch_project(p, t))
            except Exception as e:
                print(f"Error parsing combination '{combination}': {e}")
                continue
        
        # Add separator and options
        menu.add_separator()
        menu.add_command(label="📝 Bearbeiten...", 
                        command=self.show_project_task_editor)
        menu.add_command(label="📊 Session Editor...", 
                        command=self.show_session_editor)
        
        # Show menu at cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def quick_switch_project(self, project, task):
        """Quick switch to project/task with auto-split logic"""
        try:
            # Get current active session and auto-split threshold
            active_session = self.json_db.get_active_session()
            auto_split_minutes = self.json_db.config_data.get('auto_split_minutes', 5)
            
            # Check if we should auto-split the current session
            should_split = False
            if active_session and active_session.is_active:
                # Calculate elapsed time in minutes
                elapsed_seconds = int((datetime.now() - active_session.start_time).total_seconds())
                elapsed_minutes = elapsed_seconds / 60.0
                
                # Auto-split if session is running and >= threshold
                if elapsed_minutes >= auto_split_minutes:
                    should_split = True
                    print(f"🔄 Auto-splitting session after {elapsed_minutes:.1f} minutes (threshold: {auto_split_minutes})")
            
            if should_split:
                # Stop current session (creates complete session record)
                self.json_db.stop_active_session()
                
                # Create new session with new project/task
                session_type = 'break' if project == 'BREAK' else 'work'
                new_session = self.json_db.create_session(project, task, session_type)
                
                # Update UI state
                self.is_running = True
                if session_type == 'break':
                    self.play_btn.configure(text="⏸", bg='#f39c12')  # Orange for breaks
                    print(f"☕ Auto-started new break session: {project} - {task}")
                else:
                    self.play_btn.configure(text="⏸", bg='#f39c12')
                    print(f"▶️ Auto-started new work session: {project} - {task}")
                    
            else:
                # No auto-split needed - just update current session project/task
                if active_session:
                    active_session.project = project
                    active_session.task = task
                    print(f"🔄 Updated current session: {project} - {task}")
                else:
                    # No active session - user can manually start if needed
                    print(f"🔄 No active session - project/task updated: {project} - {task}")
            
            # Update current project/task state
            self.current_project = project
            self.current_task = task
            self.json_db.set_active_project_task(project, task)
            
            # Update display and save
            self.update_project_display()
            self.json_db.save_sessions()
            
        except Exception as e:
            print(f"❌ Error switching project: {e}")
    
    def update_project_display(self):
        """Update the project display label"""
        project_text = f"{self.current_project} | {self.current_task}"
        if len(project_text) > 35:
            project_text = project_text[:32] + "..."
        
        self.project_display_label.configure(text=project_text)
    
    def show_simple_session_editor(self):
        """Fallback simple session editor"""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("📝 Simple Session Editor")
        center_window(editor_window, 800, 600)  # Use global center_window function
        editor_window.transient(self.root)
        editor_window.configure(bg='#ffffff')
        
        # Create main frame
        main_frame = tk.Frame(editor_window, bg='#ffffff')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#ffffff')
        header_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(header_frame, text="📝 Simple Session Editor",
                font=('Segoe UI', 16, 'bold'), bg='#ffffff', fg='#2c3e50').pack(side='left')
        
        tk.Label(main_frame, text="⚠️ Full session editor unavailable.\nUse the main interface to manage sessions.",
                font=('Segoe UI', 12), bg='#ffffff', fg='#e74c3c', justify='center').pack(expand=True)
        
        # Close button
        tk.Button(main_frame, text="❌ Close", bg='#95a5a6', fg='white', 
                 font=('Segoe UI', 10), command=editor_window.destroy).pack(pady=20)
    
    def load_sessions_list(self, parent):
        """Load and display sessions list"""
        # Clear existing content
        for widget in parent.winfo_children():
            widget.destroy()
        
        sessions = self.json_db.sessions  # Direct access to sessions list
        
        if not sessions:
            tk.Label(parent, text="No sessions found", 
                    bg='#ffffff', fg='#7f8c8d', font=('Segoe UI', 12)).pack(pady=50)
            return
        
        # Header
        header = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        header.pack(fill='x', pady=(0, 5))
        
        tk.Label(header, text="Date", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=10).pack(side='left', padx=5, pady=5)
        tk.Label(header, text="Start", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=8).pack(side='left', padx=2)
        tk.Label(header, text="End", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=8).pack(side='left', padx=2)
        tk.Label(header, text="Project", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=12).pack(side='left', padx=5)
        tk.Label(header, text="Task", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=12).pack(side='left', padx=5)
        tk.Label(header, text="Duration", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=8).pack(side='left', padx=5)
        tk.Label(header, text="Actions", bg='#f8f9fa', font=('Segoe UI', 9, 'bold'), width=10).pack(side='left', padx=5)
        
        # Sessions
        for i, session in enumerate(sessions[-20:]):  # Show last 20 sessions
            row_color = '#ffffff' if i % 2 == 0 else '#f8f9fa'
            session_frame = tk.Frame(parent, bg=row_color, relief='solid', bd=1)
            session_frame.pack(fill='x', pady=1)
            
            date_str = session.start_time.strftime('%Y-%m-%d') if session.start_time else 'N/A'
            start_str = session.start_time.strftime('%H:%M') if session.start_time else 'N/A'
            end_str = session.end_time.strftime('%H:%M') if session.end_time else 'N/A'
            duration_str = self.json_db.format_seconds(session.duration_seconds)
            
            tk.Label(session_frame, text=date_str, bg=row_color, font=('Segoe UI', 8), width=10).pack(side='left', padx=5, pady=3)
            tk.Label(session_frame, text=start_str, bg=row_color, font=('Segoe UI', 8), width=8).pack(side='left', padx=2)
            tk.Label(session_frame, text=end_str, bg=row_color, font=('Segoe UI', 8), width=8).pack(side='left', padx=2)
            tk.Label(session_frame, text=session.project[:10], bg=row_color, font=('Segoe UI', 8), width=12).pack(side='left', padx=5)
            tk.Label(session_frame, text=session.task[:10], bg=row_color, font=('Segoe UI', 8), width=12).pack(side='left', padx=5)
            tk.Label(session_frame, text=duration_str, bg=row_color, font=('Segoe UI', 8), width=8).pack(side='left', padx=5)
            
            # Action buttons
            action_frame = tk.Frame(session_frame, bg=row_color)
            action_frame.pack(side='left', padx=5)
            
            edit_btn = tk.Button(action_frame, text="✏️", bg='#f39c12', fg='white',
                                font=('Segoe UI', 8), width=3, height=1,
                                command=lambda s=session: self.edit_session(s))
            edit_btn.pack(side='left', padx=1)
            
            delete_btn = tk.Button(action_frame, text="🗑️", bg='#e74c3c', fg='white',
                                  font=('Segoe UI', 8), width=3, height=1,
                                  command=lambda s=session: self.delete_session(s, parent))
            delete_btn.pack(side='left', padx=1)
    
    def edit_session(self, session):
        """Edit a specific session"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"✏️ Edit Session - {session.project}")
        center_window(edit_window, 520, 520)  # Use global center_window function
        edit_window.transient(self.root)
        edit_window.configure(bg='#ffffff')
        
        main_frame = tk.Frame(edit_window, bg='#ffffff')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Project
        tk.Label(main_frame, text="Project:", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        project_var = tk.StringVar(value=session.project)
        project_entry = tk.Entry(main_frame, textvariable=project_var, font=('Segoe UI', 10))
        project_entry.pack(fill='x', pady=(0, 10))
        
        # Task
        tk.Label(main_frame, text="Task:", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        task_var = tk.StringVar(value=session.task)
        task_entry = tk.Entry(main_frame, textvariable=task_var, font=('Segoe UI', 10))
        task_entry.pack(fill='x', pady=(0, 10))
        
        # Date
        tk.Label(main_frame, text="Date (YYYY-MM-DD):", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        date_var = tk.StringVar(value=session.start_time.strftime('%Y-%m-%d') if session.start_time else '')
        date_entry = tk.Entry(main_frame, textvariable=date_var, font=('Segoe UI', 10))
        date_entry.pack(fill='x', pady=(0, 10))
        
        # Start Time
        tk.Label(main_frame, text="Start Time (HH:MM:SS):", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        start_time_var = tk.StringVar(value=session.start_time.strftime('%H:%M:%S') if session.start_time else '08:00:00')
        start_time_entry = tk.Entry(main_frame, textvariable=start_time_var, font=('Segoe UI', 10))
        start_time_entry.pack(fill='x', pady=(0, 10))
        
        # End Time
        tk.Label(main_frame, text="End Time (HH:MM:SS):", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        end_time_var = tk.StringVar(value=session.end_time.strftime('%H:%M:%S') if session.end_time else '')
        end_time_entry = tk.Entry(main_frame, textvariable=end_time_var, font=('Segoe UI', 10))
        end_time_entry.pack(fill='x', pady=(0, 10))
        
        # Duration (calculated automatically but can be manually overridden)
        tk.Label(main_frame, text="Duration (minutes) - auto-calculated:", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        duration_var = tk.IntVar(value=session.duration_seconds // 60)
        duration_entry = tk.Entry(main_frame, textvariable=duration_var, font=('Segoe UI', 10))
        duration_entry.pack(fill='x', pady=(0, 10))
        
        # Helper function to calculate duration from times
        def calculate_duration():
            try:
                date_str = date_var.get()
                start_str = start_time_var.get()
                end_str = end_time_var.get()
                
                if date_str and start_str and end_str:
                    start_datetime = datetime.strptime(f"{date_str} {start_str}", '%Y-%m-%d %H:%M:%S')
                    end_datetime = datetime.strptime(f"{date_str} {end_str}", '%Y-%m-%d %H:%M:%S')
                    
                    # Handle case where end time is next day
                    if end_datetime <= start_datetime:
                        end_datetime += timedelta(days=1)
                    
                    duration_minutes = int((end_datetime - start_datetime).total_seconds() / 60)
                    duration_var.set(duration_minutes)
                    
            except Exception as e:
                print(f"Duration calculation error: {e}")
        
        # Auto-calculate button
        calc_btn = tk.Button(main_frame, text="🔄 Calculate Duration from Times",
                            bg='#3498db', fg='white', font=('Segoe UI', 9),
                            command=calculate_duration)
        calc_btn.pack(pady=(0, 15))
        
        # Note
        tk.Label(main_frame, text="Note:", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        note_var = tk.StringVar(value=session.note)
        note_entry = tk.Entry(main_frame, textvariable=note_var, font=('Segoe UI', 10))
        note_entry.pack(fill='x', pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#ffffff')
        button_frame.pack(fill='x')
        
        save_btn = tk.Button(button_frame, text="💾 Save Changes",
                            bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                            command=lambda: self.save_session_changes_extended(
                                session, project_var.get(), task_var.get(),
                                date_var.get(), start_time_var.get(), end_time_var.get(),
                                duration_var.get(), note_var.get(), edit_window))
        save_btn.pack(side='left')
        
        cancel_btn = tk.Button(button_frame, text="❌ Cancel",
                              bg='#95a5a6', fg='white', font=('Segoe UI', 10),
                              command=edit_window.destroy)
        cancel_btn.pack(side='right')
        
        print(f"✏️ Editing session: {session.project} - {session.task}")
    
    def save_session_changes_extended(self, session, project, task, date_str, start_time_str, end_time_str, duration_minutes, note, window):
        """Save extended changes to a session including times"""
        try:
            # Update basic fields
            session.project = project
            session.task = task
            session.note = note
            
            # Parse and update date/times
            if date_str and start_time_str:
                try:
                    start_datetime = datetime.strptime(f"{date_str} {start_time_str}", '%Y-%m-%d %H:%M:%S')
                    session.start_time = start_datetime
                    
                    if end_time_str:
                        end_datetime = datetime.strptime(f"{date_str} {end_time_str}", '%Y-%m-%d %H:%M:%S')
                        
                        # Handle case where end time is next day
                        if end_datetime <= start_datetime:
                            end_datetime += timedelta(days=1)
                        
                        session.end_time = end_datetime
                        
                        # Calculate duration from actual times
                        calculated_duration = int((end_datetime - start_datetime).total_seconds())
                        session.duration_seconds = calculated_duration
                        
                    else:
                        # Use manual duration
                        session.duration_seconds = duration_minutes * 60
                        if session.start_time:
                            session.end_time = session.start_time + timedelta(seconds=session.duration_seconds)
                        
                except ValueError as ve:
                    messagebox.showerror("Time Format Error", 
                                       f"Invalid time format. Use YYYY-MM-DD for date and HH:MM:SS for times.\nError: {ve}")
                    return
            else:
                # Just update duration if no time changes
                session.duration_seconds = duration_minutes * 60
            
            # Save to JSON
            self.json_db.save_sessions()
            
            messagebox.showinfo("Success", "Session updated successfully!")
            window.destroy()
            
            print(f"💾 Session updated: {project} - {task} ({duration_minutes}m)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {e}")
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
    
    def delete_session(self, session, sessions_frame):
        """Delete a session"""
        if messagebox.askyesno("Confirm Delete", f"Delete session: {session.project} - {session.task}?"):
            try:
                # Remove from sessions
                self.json_db.sessions.remove(session)
                
                # Save to JSON
                self.json_db.save_sessions()
                
                # Reload list
                self.load_sessions_list(sessions_frame)
                
                messagebox.showinfo("Success", "Session deleted successfully!")
                print(f"🗑️ Session deleted: {session.project} - {session.task}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete session: {e}")
    
    def export_all_sessions(self):
        """Export sessions with user choice"""
        try:
            # Ask user what to export
            result = messagebox.askyesnocancel("Export Options", 
                                             "Export ALL sessions?\n\n"
                                             "• Yes = Export all sessions from all days\n"
                                             "• No = Export only today's sessions\n"
                                             "• Cancel = Don't export")
            
            if result is None:  # Cancel
                return
            elif result:  # Yes - Export all
                if self.excel_report_manager.export_all(self.json_db):
                    messagebox.showinfo("Success", f"All sessions exported to {self.excel_report_manager.excel_file}")
                else:
                    messagebox.showerror("Error", "Failed to export all data")
            else:  # No - Export today only
                if self.excel_report_manager.export_all(self.json_db):
                    messagebox.showinfo("Success", f"Today's data exported to {self.excel_report_manager.excel_file}")
                else:
                    messagebox.showerror("Error", "Failed to export today's data")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def start_update_loop(self):
        """Start the update loop"""
        self.update_running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def update_loop(self):
        """Update loop"""
        while self.update_running:
            try:
                self.root.after_idle(self.update_display)
                time.sleep(1)
            except:
                break
    
    def update_display(self):
        """Update the display"""
        try:
            # Get today's work time (grün)
            work_seconds = self.json_db.get_today_work_seconds()
            work_time = self.json_db.format_seconds(work_seconds)
            self.work_time_label.config(text=work_time)
            
            # Get today's break time (orange)
            break_seconds = self.json_db.get_today_break_seconds()
            break_time = self.json_db.format_seconds(break_seconds)
            self.break_time_label.config(text=break_time)
            
            # Calculate remaining work time (schwarz)
            # Formula: remaining = required_work_hours - (worked_hours - break_hours)
            required_work_seconds = self.json_db.get_today_required_work_seconds()
            net_work_seconds = work_seconds - break_seconds  # Actual productive work time
            remaining_seconds = max(0, required_work_seconds - net_work_seconds)
            remaining_time = self.json_db.format_seconds(remaining_seconds)
            self.remaining_time_label.config(text=remaining_time)
            
            # Update current session timer (violet)
            active_session = self.json_db.get_active_session()
            if active_session and active_session.is_active:
                # Calculate current session duration
                current_session_seconds = int((datetime.now() - active_session.start_time).total_seconds())
                current_session_time = self.json_db.format_seconds(current_session_seconds)
                self.current_session_label.config(text=current_session_time)
            else:
                # No active session
                self.current_session_label.config(text="00:00")
            
            # Update project display
            self.update_project_display()
            
            # Update button state
            active_session = self.json_db.get_active_session()
            if active_session and active_session.session_type == 'work':
                if not self.is_running:
                    self.is_running = True
                    self.play_btn.configure(text="⏸", bg='#f39c12')
            else:
                if self.is_running:
                    self.is_running = False
                    self.play_btn.configure(text="▶", bg='#27ae60')
                    
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def on_window_configure(self, event):
        """Handle window configuration changes (position, size)"""
        # Only handle events for the main window, not child widgets
        if event.widget == self.root:
            # Cancel any pending save operation
            if hasattr(self, '_save_timer'):
                self.root.after_cancel(self._save_timer)
            
            # Schedule position save with longer delay to reduce frequency
            self._save_timer = self.root.after(2000, self.save_position)  # 2 seconds delay
    
    def save_position(self):
        """Save current window position to config"""
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            
            # Only save if position actually changed
            config = self.json_db.config_data
            current_pos = config.get('overlay_settings', {}).get('position', {})
            
            if current_pos.get('x') == x and current_pos.get('y') == y:
                return  # Position hasn't changed, don't save
            
            # Update overlay_settings position
            if 'overlay_settings' not in config:
                config['overlay_settings'] = {}
            config['overlay_settings']['position'] = {'x': x, 'y': y}
            
            # Also update overlay position for compatibility
            if 'overlay' not in config:
                config['overlay'] = {}
            config['overlay']['position'] = {'x': x, 'y': y}
            
            self.json_db.save_config()
            print(f"💾 Position saved: x={x}, y={y}")
            
        except Exception as e:
            print(f"❌ Error saving position: {e}")

    def on_closing(self):
        """Handle window closing"""
        try:
            # Save position
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            
            config = self.json_db.config_data
            if 'overlay_settings' not in config:
                config['overlay_settings'] = {}
            config['overlay_settings']['position'] = {'x': x, 'y': y}
            self.json_db.save_config()
            
            # Stop active session if needed and export to Excel
            active_session = self.json_db.get_active_session()
            if active_session:
                # Stop the session without asking
                stopped_session = self.json_db.stop_active_session()
                self.json_db.save_sessions()
                
                if stopped_session:
                    duration = self.json_db.format_seconds(stopped_session.duration_seconds)
                    print(f"⏹️ Auto-stopped: {stopped_session.project} - {stopped_session.task} ({duration})")
            
            # Always export to Excel when closing
            try:
                if self.excel_report_manager.export_all(self.json_db):
                    print(f"📊 Excel exported: {self.excel_report_manager.excel_file}")
                else:
                    print("⚠️ Excel export had no data or failed")
            except Exception as export_error:
                print(f"❌ Excel export error: {export_error}")
            
            self.update_running = False
            
        except Exception as e:
            print(f"Error during closing: {e}")
        finally:
            self.root.quit()
            self.root.destroy()
