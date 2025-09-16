"""
Session Editor Module

Provides a GUI interface for editing and managing work sessions and breaks with sorting and filtering.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from utils.time_utils import format_timedelta
from utils.window_utils import center_window, get_optimal_dialog_size
from core.excel_report_manager import ExcelReportManager
from typing import List, Dict, Optional


class SessionEditor:
    def __init__(self, parent, json_db, callback=None):
        self.parent = parent
        self.json_db = json_db  # Use JsonDatabase directly instead of SessionManager
        self.callback = callback  # Callback to update overlay
        # Direct Excel report manager (replaces removed ExcelExporter)
        self.excel_report_manager = ExcelReportManager(
            json_db.config_data.get('excel_file', 'working_hours.xlsx')
        )
        self.sessions = []
        self.dialog = None
        self.current_sessions = []  # Store current sessions for filtering/sorting
        self.sort_column = None
        self.sort_reverse = False
    
    def create_modern_button(self, parent, text, bg_color, hover_color, command):
        """Create a modern styled button matching BeautifulCleanOverlay design"""
        btn = tk.Button(parent, text=text, bg=bg_color, fg='white',
                       font=('Segoe UI', 9, 'bold'), bd=0, cursor='hand2',
                       activebackground=hover_color, activeforeground='white',
                       relief='flat', padx=15, pady=8, command=command)
        
        # Add hover effects
        def on_enter(e):
            btn.configure(bg=hover_color)
        
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn

    def show_session_editor(self):
        """Show the session editor dialog with modern design and filtering"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            return
        
        # Create modern dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("📝 Session Manager")
        self.dialog.configure(bg='#ffffff')
        self.dialog.resizable(True, True)
        
        # Setup dialog relationships before positioning
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Get optimal size and center the window AFTER configuration
        width, height = get_optimal_dialog_size('session_editor')
        center_window(self.dialog, width, height)
        
        print(f"📝 Session Editor window created and centered")
        
        # Create the UI
        self.create_editor_ui()
        
        # Load sessions
        self.load_all_sessions()
        
        # Focus the dialog
        self.dialog.focus_set()

    def create_editor_ui(self):
        """Creates the modern user interface with filtering and sorting"""
        # Main container with modern background
        main_frame = tk.Frame(self.dialog, bg='#f8f9fa', relief='flat', bd=0)
        main_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Header section with modern styling
        header_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='flat', bd=0)
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        # Title label
        title_label = tk.Label(header_frame, text="📅 Session Manager", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg='#f8f9fa', fg='#2c3e50')
        title_label.pack(side='left', anchor='w')
        
        # Date info
        today = datetime.now().strftime("%d.%m.%Y")
        date_label = tk.Label(header_frame, text=f"Today: {today}", 
                             font=('Segoe UI', 11), 
                             bg='#f8f9fa', fg='#7f8c8d')
        date_label.pack(side='right', anchor='e')
        
        # Filter section
        filter_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='flat', bd=0)
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Day filter
        filter_left = tk.Frame(filter_frame, bg='#f8f9fa')
        filter_left.pack(side='left', fill='x', expand=True)
        
        tk.Label(filter_left, text="🔍 Day Filter:", 
                font=('Segoe UI', 9, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').pack(side='left')
        
        self.day_filter_var = tk.StringVar(value="Today")  # Default to Today instead of All Days
        self.day_filter_combo = ttk.Combobox(filter_left, textvariable=self.day_filter_var,
                                            font=('Segoe UI', 9), width=15,
                                            state='readonly')
        self.day_filter_combo.pack(side='left', padx=(5, 10))
        self.day_filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
        # Right side of filter frame - Refresh button and sorting info
        filter_right = tk.Frame(filter_frame, bg='#f8f9fa')
        filter_right.pack(side='right')
        
        # Refresh button in top right
        refresh_btn = self.create_modern_button(filter_right, "🔄 Refresh", 
                                               '#95a5a6', '#7f8c8d', self.load_all_sessions)
        refresh_btn.pack(side='right', padx=(0, 10))
        
        # Sorting info
        sort_info = tk.Label(filter_right, text="💡 Click column headers to sort", 
                           font=('Segoe UI', 9), 
                           bg='#f8f9fa', fg='#7f8c8d')
        sort_info.pack(side='right')
        
        # Sessions container with modern styling
        sessions_frame = tk.Frame(main_frame, bg='#ffffff', relief='flat', bd=0)
        sessions_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview container
        tree_container = tk.Frame(sessions_frame, bg='#ffffff')
        tree_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Columns for session data (add Task column between Project and Note)
        columns = ("Date", "Day", "Start", "End", "Duration", "Project", "Task", "Note")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        
        # Configure columns with modern headings and sorting
        self.tree.heading("Date", text="📅 Date", command=lambda: self.sort_by_column("Date"))
        self.tree.heading("Day", text="📅 Day", command=lambda: self.sort_by_column("Day"))
        self.tree.heading("Start", text="🕐 Start", command=lambda: self.sort_by_column("Start"))
        self.tree.heading("End", text="🕑 End", command=lambda: self.sort_by_column("End")) 
        self.tree.heading("Duration", text="⏱️ Duration", command=lambda: self.sort_by_column("Duration"))
        self.tree.heading("Project", text="📁 Project", command=lambda: self.sort_by_column("Project"))
        self.tree.heading("Task", text="📋 Task", command=lambda: self.sort_by_column("Task"))
        self.tree.heading("Note", text="📝 Note", command=lambda: self.sort_by_column("Note"))
        
        # Set column widths
        self.tree.column("Date", width=80, minwidth=70)
        self.tree.column("Day", width=80, minwidth=70)
        self.tree.column("Start", width=70, minwidth=60)
        self.tree.column("End", width=70, minwidth=60)
        self.tree.column("Duration", width=80, minwidth=70)
        self.tree.column("Project", width=120, minwidth=100)
        self.tree.column("Task", width=120, minwidth=100)
        self.tree.column("Note", width=200, minwidth=150)
        
        # Modern scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack treeview and scrollbar (only vertical)
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        # Action buttons with modern styling
        button_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='flat', bd=0)
        button_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Left button group - Actions
        left_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        left_buttons.pack(side='left', fill='x', expand=True)
        
        # Create modern buttons
        add_btn = self.create_modern_button(left_buttons, "➕ Add Session", 
                                           '#27ae60', '#229954', self.add_session)
        add_btn.pack(side='left', padx=(0, 8))
        
        break_btn = self.create_modern_button(left_buttons, "☕ Add Break", 
                                             '#f39c12', '#e67e22', self.add_break)
        break_btn.pack(side='left', padx=(0, 8))
        
        edit_btn = self.create_modern_button(left_buttons, "✏️ Edit", 
                                            '#3498db', '#2980b9', self.edit_selected)
        edit_btn.pack(side='left', padx=(0, 8))
        
        delete_btn = self.create_modern_button(left_buttons, "🗑️ Delete", 
                                              '#e74c3c', '#c0392b', self.delete_selected)
        delete_btn.pack(side='left')
        
        # Right button group - Utility
        right_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        right_buttons.pack(side='right')
        
        # Close button positioned far right
        close_btn = self.create_modern_button(right_buttons, "❌ Close", 
                                             '#95a5a6', '#7f8c8d', self.dialog.destroy)
        close_btn.pack(side='right', padx=(8, 0))
        
        excel_btn = self.create_modern_button(right_buttons, "📊 Export Excel", 
                                             '#3498db', '#2980b9', self.export_to_excel)
        excel_btn.pack(side='right', padx=(8, 0))
        
        save_btn = self.create_modern_button(right_buttons, "💾 Save", 
                                            '#27ae60', '#229954', self.save_sessions)
        save_btn.pack(side='right', padx=(8, 0))
        
        # Status bar with modern styling
        status_frame = tk.Frame(main_frame, bg='#ecf0f1', relief='flat', bd=0, height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready • Use double-click to edit sessions", 
                                   font=('Segoe UI', 9), bg='#ecf0f1', fg='#7f8c8d')
        self.status_label.pack(side='left', padx=20, pady=5)
        
        # Event bindings
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        
        # Keyboard shortcuts
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<F2>", lambda e: self.edit_selected())
        self.tree.bind("<Return>", lambda e: self.edit_selected())
        
        # Mouse wheel scrolling
        self.tree.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        self.tree.bind("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.tree.bind("<Button-5>", self._on_mousewheel)    # Linux scroll down
        
        # Dialog-wide shortcuts
        self.dialog.bind("<MouseWheel>", self._on_mousewheel)
        self.dialog.bind("<Delete>", lambda e: self.delete_selected())
        self.dialog.bind("<F2>", lambda e: self.edit_selected())
        self.dialog.bind("<Return>", lambda e: self.edit_selected())
        self.dialog.bind("<Control-n>", lambda e: self.add_session())
        self.dialog.bind("<Control-b>", lambda e: self.add_break())
        self.dialog.bind("<F5>", lambda e: self.load_all_sessions())
        self.dialog.bind("<Control-s>", lambda e: self.save_sessions())

    def sort_by_column(self, col):
        """Sort sessions by the specified column"""
        if not self.current_sessions:
            return
        
        # Toggle sort direction if same column clicked
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = col
        
        # Update column header to show sort direction
        for column in ("Date", "Day", "Start", "End", "Duration", "Project", "Note"):
            if column == col:
                direction = " ⬇️" if self.sort_reverse else " ⬆️"
                current_text = self.tree.heading(column)['text']
                base_text = current_text.split(' ⬇️')[0].split(' ⬆️')[0]
                self.tree.heading(column, text=base_text + direction)
            else:
                # Remove direction indicators from other columns
                current_text = self.tree.heading(column)['text'] 
                base_text = current_text.split(' ⬇️')[0].split(' ⬆️')[0]
                self.tree.heading(column, text=base_text)
        
        # Sort the sessions
        try:
            def sort_key(session):
                if col == "Date":
                    return session.start_time.date()
                elif col == "Day":
                    return session.start_time.strftime("%A")
                elif col == "Start":
                    return session.start_time.strftime("%H:%M")
                elif col == "End":
                    return session.end_time.strftime("%H:%M") if session.end_time else "99:99"
                elif col == "Duration":
                    return session.duration_seconds
                elif col == "Project":
                    return session.project
                elif col == "Note":
                    return getattr(session, 'note', '')
                return ""
            
            self.current_sessions.sort(key=sort_key, reverse=self.sort_reverse)
            self.populate_treeview(self.current_sessions)
            
            # Update status
            direction_text = "descending" if self.sort_reverse else "ascending"
            self.status_label.config(text=f"Sorted by {col} ({direction_text})")
            
        except Exception as e:
            print(f"❌ Error sorting by {col}: {e}")
            self.status_label.config(text=f"Error sorting by {col}")

    def apply_filter(self, event=None):
        """Apply day filter to sessions"""
        selected_day = self.day_filter_var.get()
        
        if selected_day == "All Days":
            filtered_sessions = self.sessions
        elif selected_day == "Today":
            from datetime import date
            today = date.today()
            filtered_sessions = [
                session for session in self.sessions
                if session.start_time.date() == today
            ]
        elif selected_day == "---":
            # Ignore separator
            filtered_sessions = self.sessions
        elif "(" in selected_day and ")" in selected_day:
            # Handle "Day (MM/DD)" format
            day_part = selected_day.split(" (")[0]
            filtered_sessions = [
                session for session in self.sessions
                if session.start_time.strftime("%A") == day_part
            ]
        else:
            # Handle regular day names
            filtered_sessions = [
                session for session in self.sessions
                if session.start_time.strftime("%A") == selected_day
            ]
        
        self.current_sessions = filtered_sessions
        self.populate_treeview(filtered_sessions)
        
        # Update status
        if selected_day == "All Days":
            self.status_label.config(text=f"Showing all {len(filtered_sessions)} sessions")
        else:
            self.status_label.config(text=f"Filtered by {selected_day}: {len(filtered_sessions)} sessions")

    def update_day_filter_options(self):
        """Update the day filter dropdown with available days and dates"""
        if not self.sessions:
            self.day_filter_combo['values'] = ["All Days"]
            return
        
        # Get unique days and dates from sessions
        days_with_dates = set()
        dates_map = {}  # Map day names to actual dates
        
        for session in self.sessions:
            session_date = session.start_time.date()
            day_name = session.start_time.strftime("%A")
            date_str = session_date.strftime("%Y-%m-%d")
            
            days_with_dates.add(day_name)
            if day_name not in dates_map:
                dates_map[day_name] = []
            if date_str not in dates_map[day_name]:
                dates_map[day_name].append(date_str)
        
        # Create filter options
        filter_options = ["All Days"]
        
        # Add "Today" option if we have today's sessions
        from datetime import date
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        has_today = any(session.start_time.date() == today for session in self.sessions)
        if has_today:
            filter_options.append("Today")
        
        # Add days of week
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        available_days = [day for day in weekday_order if day in days_with_dates]
        filter_options.extend(available_days)
        
        # Add recent dates (last 7 days)
        recent_dates = set()
        for session in self.sessions:
            days_ago = (today - session.start_time.date()).days
            if 0 <= days_ago <= 7:
                date_str = session.start_time.date().strftime("%m/%d")
                recent_dates.add(f"{session.start_time.strftime('%A')} ({date_str})")
        
        if recent_dates:
            filter_options.append("---")  # Separator
            filter_options.extend(sorted(recent_dates))
        
        self.day_filter_combo['values'] = filter_options
        
        # Reset to "Today" if current selection is not in new list, but "Today" is available
        current_selection = self.day_filter_var.get()
        if current_selection not in filter_options:
            if "Today" in filter_options:
                self.day_filter_var.set("Today")  # Prefer Today over All Days
            else:
                self.day_filter_var.set("All Days")  # Fallback to All Days

    def populate_treeview(self, sessions_to_show):
        """Populate the treeview with sessions"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add sessions to treeview
        for session in sessions_to_show:
            try:
                date_str = session.start_time.strftime("%m/%d")
                day = session.start_time.strftime("%A")
                start_time = session.start_time.strftime("%H:%M")
                end_time = session.end_time.strftime("%H:%M") if session.end_time else "Active"
                duration = format_timedelta(timedelta(seconds=session.duration_seconds))
                project = session.project
                task = getattr(session, 'task', '')  # Task field
                note = getattr(session, 'note', '')
                
                self.tree.insert("", "end", values=(date_str, day, start_time, end_time, duration, project, task, note))
            except Exception as e:
                print(f"❌ Error adding session to treeview: {e}")

    def load_all_sessions(self):
        """Load all sessions from the database (not just today)"""
        try:
            print("📖 SessionEditor: Loading all sessions from JsonDatabase...")
            
            # Get ALL sessions from JsonDatabase (not just today)
            all_sessions = self.json_db.sessions
            self.sessions = all_sessions
            self.current_sessions = all_sessions[:]  # Copy for filtering
            
            print(f"📊 SessionEditor: Found {len(all_sessions)} total sessions")
            
            # Debug session loading
            for i, session in enumerate(all_sessions[:5]):  # Show first 5 for debugging
                print(f"🔍 Loading session {i}: {session.project} - {session.start_time.strftime('%Y-%m-%d %H:%M')}")
            
            if len(all_sessions) > 5:
                print(f"... and {len(all_sessions) - 5} more sessions")
            
            # Update filter options
            self.update_day_filter_options()
            
            # Apply current filter
            self.apply_filter()
            
            print("✅ SessionEditor: Loaded all sessions successfully")
            
        except Exception as e:
            print(f"❌ SessionEditor Error loading sessions: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load sessions: {e}")

    def save_sessions(self):
        """Save all sessions and export to Excel"""
        try:
            # Save sessions to JSON
            self.json_db.save_sessions()
            
            # Export to Excel
            success = self.excel_report_manager.export_all(self.json_db)
            
            if success:
                self.status_label.config(text="✅ Sessions saved & Excel updated")
                print("💾 SessionEditor: Sessions saved and Excel exported")
            else:
                self.status_label.config(text="✅ Sessions saved (Excel export failed)")
                print("💾 SessionEditor: Sessions saved, but Excel export failed")
                
        except Exception as e:
            self.status_label.config(text="❌ Error saving sessions")
            print(f"❌ SessionEditor Error saving: {e}")
            messagebox.showerror("Error", f"Failed to save sessions: {e}")

    def export_to_excel(self):
        """Export sessions to Excel with user choice"""
        try:
            # Ask user what to export (same as in overlay)
            result = messagebox.askyesnocancel("Export Options", 
                                             "Export ALL sessions?\n\n"
                                             "• Yes = Export all sessions from all days\n"
                                             "• No = Export only today's sessions\n"
                                             "• Cancel = Don't export")
            
            if result is None:  # Cancel
                return
            elif result:  # Yes - Export all
                if self.excel_report_manager.export_all(self.json_db):
                    self.status_label.config(text="✅ All sessions exported to Excel")
                    messagebox.showinfo("Success", f"All sessions exported to {self.excel_report_manager.excel_file}")
                    print("📊 SessionEditor: All sessions exported to Excel")
                else:
                    self.status_label.config(text="❌ Excel export failed")
                    messagebox.showerror("Error", "Failed to export all data")
            else:  # No - Export today only
                if self.excel_report_manager.export_all(self.json_db):  # Today-only simplified to full export
                    self.status_label.config(text="✅ Today's sessions exported to Excel")
                    messagebox.showinfo("Success", f"Today's data exported to {self.excel_report_manager.excel_file}")
                    print("📊 SessionEditor: Today's sessions (full export) written to Excel")
                else:
                    self.status_label.config(text="❌ Excel export failed")
                    messagebox.showerror("Error", "Failed to export today's data")
        except Exception as e:
            self.status_label.config(text="❌ Excel export error")
            messagebox.showerror("Error", f"Export failed: {e}")
            print(f"❌ SessionEditor Excel export error: {e}")

    def add_session(self):
        """Add a new work session"""
        self.show_session_dialog()

    def add_break(self):
        """Add a new break session"""
        self.show_session_dialog(session_type="break")

    def edit_selected(self):
        """Edit the selected session"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a session to edit.")
            return
        
        # Find the session based on the selected item
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if len(values) >= 6:
            date_str, day, start_time, end_time, duration, project = values[:6]
            
            # Find matching session
            for session in self.current_sessions:
                if (session.start_time.strftime("%m/%d") == date_str and
                    session.start_time.strftime("%A") == day and
                    session.start_time.strftime("%H:%M") == start_time and
                    session.project == project):
                    self.show_session_dialog(session)
                    break

    def delete_selected(self):
        """Delete the selected session"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a session to delete.")
            return
        
        if messagebox.askyesno("Delete Session", "Are you sure you want to delete the selected session?"):
            item = selection[0]
            values = self.tree.item(item)["values"]
            
            if len(values) >= 6:
                date_str, day, start_time, end_time, duration, project = values[:6]
                
                # Find and remove matching session
                session_to_delete = None
                for session in self.current_sessions:
                    if (session.start_time.strftime("%m/%d") == date_str and
                        session.start_time.strftime("%A") == day and
                        session.start_time.strftime("%H:%M") == start_time and
                        session.project == project):
                        session_to_delete = session
                        break
                
                if session_to_delete:
                    # Remove from database
                    print(f"🗑️ Removing session: {session_to_delete.project} - {session_to_delete.task}")
                    self.json_db.remove_session(session_to_delete.id)
                    
                    # Reload all sessions from database to ensure consistency
                    self.load_all_sessions()
                    
                    self.status_label.config(text="🗑️ Session deleted")
                else:
                    self.status_label.config(text="❌ Session not found")

    def show_session_dialog(self, session=None, session_type="work"):
        """Show dialog for adding/editing a session"""
        dialog = tk.Toplevel(self.dialog)
        
        # Check if this is an active session
        is_active_session = session and (session.is_active or session.end_time is None)
        
        if session:
            if is_active_session:
                dialog.title("� Edit Active Session")
            else:
                dialog.title("📝 Edit Session")
        else:
            dialog.title("➕ Add Session")
            
        # Configure dialog properties first - PREVENTS BLINKING
        dialog.configure(bg='#ffffff')
        dialog.resizable(True, True)  # Make dialog resizable
        dialog.minsize(400, 350)      # Set minimum size
        
        # Setup dialog relationships
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        # Use centered window with optimal size - NO MORE MANUAL GEOMETRY
        height = 400 if is_active_session else 370
        center_window(dialog, 450, height)
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#ffffff', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Configure grid weights for resizing
        main_frame.grid_columnconfigure(1, weight=1)  # Column 1 (input fields) expands
        
        # Determine note row position
        if is_active_session:
            note_row = 6
        else:
            note_row = 5
            
        # Set row weight for note field (expandable)
        main_frame.grid_rowconfigure(note_row, weight=1)  # Note row expands
        
        # Form fields
        fields = {}
        
        # Get available projects and tasks
        available_projects = self.json_db.get_available_projects()
        if not available_projects:
            available_projects = ['General', 'Web Development', 'Documentation']
        
        # Project dropdown
        tk.Label(main_frame, text="Project:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        project_var = tk.StringVar(value=session.project if session else available_projects[0])
        project_combo = ttk.Combobox(main_frame, textvariable=project_var, 
                                   values=available_projects, 
                                   font=('Segoe UI', 10), width=35, state='readonly')
        project_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        fields['project'] = project_var
        
        # Task dropdown
        tk.Label(main_frame, text="Task:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)
        
        task_var = tk.StringVar()
        task_combo = ttk.Combobox(main_frame, textvariable=task_var, 
                                font=('Segoe UI', 10), width=35, state='readonly')
        task_combo.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        fields['task'] = task_var
        
        # Function to update tasks when project changes
        def update_tasks(*args):
            selected_project = project_var.get()
            if selected_project:
                tasks = self.json_db.get_tasks_for_project(selected_project)
                if not tasks:
                    tasks = ['Daily Work']
                task_combo['values'] = tasks
                
                # Set initial task value
                if session and session.project == selected_project:
                    task_var.set(session.task if session.task in tasks else tasks[0])
                else:
                    task_var.set(tasks[0])
        
        # Bind project change event
        project_var.trace('w', update_tasks)
        
        # Initialize tasks for the selected project
        update_tasks()
        
        # Date
        tk.Label(main_frame, text="Date:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff', fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=5)
        date_value = session.start_time.strftime("%Y-%m-%d") if session else datetime.now().strftime("%Y-%m-%d")
        fields['date'] = tk.StringVar(value=date_value)
        tk.Entry(main_frame, textvariable=fields['date'], font=('Segoe UI', 10),
                width=37).grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Start Time
        tk.Label(main_frame, text="Start Time:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff', fg='#2c3e50').grid(row=3, column=0, sticky='w', pady=5)
        fields['start_time'] = tk.StringVar(
            value=session.start_time.strftime("%H:%M") if session else datetime.now().strftime("%H:%M"))
        tk.Entry(main_frame, textvariable=fields['start_time'], font=('Segoe UI', 10),
                width=37).grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # End Time (with different handling for active sessions)
        end_time_label_text = "End Time:" if not is_active_session else "End Time (optional):"
        tk.Label(main_frame, text=end_time_label_text, font=('Segoe UI', 10, 'bold'),
                bg='#ffffff', fg='#2c3e50').grid(row=4, column=0, sticky='w', pady=5)
        
        # For active sessions, end time should be empty or current time
        if is_active_session:
            end_time_value = ""  # Empty for active sessions
        else:
            end_time_value = (session.end_time.strftime("%H:%M") if session and session.end_time 
                            else (datetime.now() + timedelta(hours=1)).strftime("%H:%M"))
        
        fields['end_time'] = tk.StringVar(value=end_time_value)
        end_time_entry = tk.Entry(main_frame, textvariable=fields['end_time'], font=('Segoe UI', 10),
                                width=37)
        end_time_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Add help text for active sessions
        if is_active_session:
            help_label = tk.Label(main_frame, text="💡 Leave end time empty to keep session running", 
                                font=('Segoe UI', 8), bg='#ffffff', fg='#7f8c8d', justify='left')
            help_label.grid(row=5, column=1, sticky='w', pady=(0, 5), padx=(10, 0))
        
        # Note (mehrzeilig)
        tk.Label(main_frame, text="Note:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff', fg='#2c3e50').grid(row=note_row, column=0, sticky='nw', pady=5)
        
        # Frame für mehrzeiliges Note-Feld mit Scrollbar
        note_frame = tk.Frame(main_frame, bg='#ffffff')
        note_frame.grid(row=note_row, column=1, sticky='nsew', pady=5, padx=(10, 0))
        note_frame.grid_columnconfigure(0, weight=1)
        note_frame.grid_rowconfigure(0, weight=1)
        
        # Mehrzeiliges Text-Widget für Notes
        fields['note_text'] = tk.Text(note_frame, font=('Segoe UI', 10),
                                     width=37, height=4, wrap=tk.WORD,
                                     relief='solid', bd=1)
        fields['note_text'].grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar für das Text-Widget
        note_scrollbar = tk.Scrollbar(note_frame, orient='vertical', command=fields['note_text'].yview)
        note_scrollbar.grid(row=0, column=1, sticky='ns')
        fields['note_text'].configure(yscrollcommand=note_scrollbar.set)
        
        # Note-Inhalt laden
        if session and hasattr(session, 'note') and session.note:
            fields['note_text'].insert('1.0', session.note)
        
        # StringVar für Kompatibilität (wird für das Speichern benötigt)
        fields['note'] = tk.StringVar(value=getattr(session, 'note', '') if session else "")
        
        # Add quick project/task buttons
        quick_frame = tk.Frame(main_frame, bg='#ffffff')
        quick_frame.grid(row=note_row + 1, column=0, columnspan=2, sticky='ew', pady=10)
        
        def add_new_project():
            """Add a new project"""
            project_name = simpledialog.askstring("New Project", "Enter project name:")
            if project_name and project_name.strip():
                project_name = project_name.strip()
                if self.json_db.add_new_project(project_name):
                    # Update project dropdown
                    new_projects = self.json_db.get_available_projects()
                    project_combo['values'] = new_projects
                    project_var.set(project_name)
                    
        def add_new_task():
            """Add a new task to current project"""
            current_project = project_var.get()
            if not current_project:
                messagebox.showwarning("No Project", "Please select a project first.")
                return
                
            task_name = simpledialog.askstring("New Task", f"Enter task name for '{current_project}':")
            if task_name and task_name.strip():
                task_name = task_name.strip()
                if self.json_db.add_task_to_project(current_project, task_name):
                    # Update tasks dropdown
                    update_tasks()
                    task_var.set(task_name)
        
        # Quick action buttons
        new_project_btn = self.create_modern_button(quick_frame, "➕ New Project", 
                                                   '#3498db', '#2980b9', add_new_project)
        new_project_btn.pack(side='left', padx=(0, 5))
        
        new_task_btn = self.create_modern_button(quick_frame, "➕ New Task", 
                                                '#9b59b6', '#8e44ad', add_new_task)
        new_task_btn.pack(side='left')
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#ffffff')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        def save_session():
            try:
                project = fields['project'].get().strip()
                task = fields['task'].get().strip()
                date_str = fields['date'].get().strip()
                start_str = fields['start_time'].get().strip()
                end_str = fields['end_time'].get().strip()
                
                # Get note from Text widget
                note = fields['note_text'].get('1.0', 'end-1c').strip()
                
                if not project:
                    messagebox.showerror("Error", "Project is required")
                    return
                
                # Parse date
                try:
                    session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD format.")
                    return
                
                # Parse start time using the specified date
                start_time = datetime.combine(session_date, datetime.strptime(start_str, "%H:%M").time())
                
                # Handle end time based on session type and input
                end_time = None
                duration = 0
                
                if end_str.strip():  # If end time is provided
                    end_time = datetime.combine(session_date, datetime.strptime(end_str, "%H:%M").time())
                    
                    if end_time <= start_time:
                        messagebox.showerror("Error", "End time must be after start time")
                        return
                    
                    duration = (end_time - start_time).total_seconds()
                elif session and not is_active_session:
                    # For completed sessions, end time is required
                    messagebox.showerror("Error", "End time is required for completed sessions")
                    return
                
                if session:
                    # Update existing session
                    session.project = project
                    session.task = task
                    session.start_time = start_time
                    
                    if end_time:
                        # End time provided - mark session as completed
                        session.end_time = end_time
                        session.duration_seconds = int(duration)
                        session.is_active = False
                    else:
                        # No end time - keep session active
                        session.end_time = None
                        session.is_active = True
                        # For active sessions, calculate duration from start to now
                        current_duration = (datetime.now() - start_time).total_seconds()
                        session.duration_seconds = int(max(0, current_duration))
                    
                    session.note = note
                    self.json_db.update_session(session)
                else:
                    # Create new session
                    if end_time:
                        # Complete session
                        self.json_db.add_session(
                            start_time=start_time,
                            end_time=end_time,
                            project=project,
                            task=task,
                            session_type=session_type,
                            note=note
                        )
                    else:
                        # Active session
                        new_session = self.json_db.create_session(project, task, session_type)
                        new_session.start_time = start_time
                        new_session.note = note
                        self.json_db.update_session(new_session)
                
                dialog.destroy()
                self.load_all_sessions()  # Refresh the display
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid time format. Use HH:MM format.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save session: {e}")
        
        save_btn = self.create_modern_button(button_frame, "💾 Save", 
                                            '#27ae60', '#229954', save_session)
        save_btn.pack(side='right', padx=(5, 0))
        
        cancel_btn = self.create_modern_button(button_frame, "❌ Cancel", 
                                              '#95a5a6', '#7f8c8d', dialog.destroy)
        cancel_btn.pack(side='right')

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            context_menu = tk.Menu(self.dialog, tearoff=0)
            context_menu.add_command(label="✏️ Edit", command=self.edit_selected)
            context_menu.add_command(label="🗑️ Delete", command=self.delete_selected)
            context_menu.add_separator()
            context_menu.add_command(label="🔄 Refresh", command=self.load_all_sessions)
            
            context_menu.tk_popup(event.x_root, event.y_root)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        try:
            if event.delta:
                # Windows
                delta = -1 * (event.delta / 120)
            else:
                # Linux
                if event.num == 4:
                    delta = -1
                elif event.num == 5:
                    delta = 1
                else:
                    return
            
            self.tree.yview_scroll(int(delta), "units")
        except Exception as e:
            print(f"Mouse wheel error: {e}")
