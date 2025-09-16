"""
UI services for managing dialogs, windows, and user interface operations.

This module provides centralized UI management services,
extracting UI logic from main application classes.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Any, List, Callable, Optional
from utils.time_utils import format_timedelta
from utils.window_utils import center_window, get_optimal_dialog_size


class DialogService:
    """
    Service for managing application dialogs and popups.
    
    Centralizes dialog creation and management to improve
    code reusability and maintainability.
    """
    
    def __init__(self, parent_window):
        """
        Initialize dialog service.
        
        Args:
            parent_window: Parent window for dialogs
        """
        self.parent = parent_window
        self.active_dialogs = {}
    
    def create_session_info_dialog(
        self, 
        is_working: bool,
        current_project: str,
        current_session_project: Optional[str],
        current_session_note: Optional[str],
        start_time: Optional[Any],
        total_work_time: Any,
        project_list: List[str],
        save_callback: Callable,
        cancel_callback: Callable
    ) -> None:
        """
        Create session information dialog.
        
        Args:
            is_working: Whether currently working
            current_project: Current active project
            current_session_project: Project of current session
            current_session_note: Note of current session
            start_time: Session start time
            total_work_time: Total work time today
            project_list: Available projects
            save_callback: Function to call when saving
            cancel_callback: Function to call when canceling
        """
        dialog = tk.Toplevel(self.parent)
        dialog.title("Session Information")
        center_window(dialog, 500, 400)
        dialog.resizable(False, False)
        
        # Status information
        if is_working and start_time:
            from datetime import datetime
            current_duration = datetime.now() - start_time
            info_text = f"Laufende Session seit: {start_time.strftime('%H:%M')}\n"
            info_text += f"Aktuelle Dauer: {format_timedelta(current_duration)}\n"
            info_text += f"Aktuelles Projekt: {current_project}"
            info_color = "green"
        else:
            info_text = f"Keine laufende Session\n"
            info_text += f"Heutige Arbeitszeit: {format_timedelta(total_work_time)}\n"
            info_text += f"Aktuelles Projekt: {current_project}"
            info_color = "blue"
        
        info_label = tk.Label(dialog, text=info_text, font=("Arial", 10), fg=info_color)
        info_label.pack(pady=10)
        
        # Project selection
        project_frame = tk.Frame(dialog)
        project_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(project_frame, text="Projekt:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        project_var = tk.StringVar(value=current_session_project or current_project)
        project_combo = ttk.Combobox(
            project_frame,
            textvariable=project_var,
            values=project_list,
            state="readonly",
            width=40
        )
        project_combo.pack(pady=5, fill="x")
        
        # Note input
        note_label_text = "Session-Notiz:" if is_working else "Standard-Notiz (für neue Sessions):"
        tk.Label(dialog, text=note_label_text, font=("Arial", 10)).pack(anchor="w", padx=10)
        
        note_text = tk.Text(dialog, height=8, width=45, wrap=tk.WORD)
        note_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Insert existing note
        if is_working and current_session_note:
            note_text.insert("1.0", current_session_note)
        elif not is_working:
            # Placeholder for when no session is running
            placeholder = "Hier können Sie eine Standard-Notiz eingeben, die für neue Sessions verwendet wird..."
            note_text.insert("1.0", placeholder)
            note_text.config(fg="gray")
            
            def on_focus_in(event):
                if note_text.get("1.0", tk.END).strip() == placeholder:
                    note_text.delete("1.0", tk.END)
                    note_text.config(fg="black")
            
            def on_focus_out(event):
                if not note_text.get("1.0", tk.END).strip():
                    note_text.insert("1.0", placeholder)
                    note_text.config(fg="gray")
            
            note_text.bind("<FocusIn>", on_focus_in)
            note_text.bind("<FocusOut>", on_focus_out)
        
        note_text.focus()
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def on_save():
            new_note = note_text.get("1.0", tk.END).strip()
            new_project = project_var.get()
            save_callback(new_project, new_note)
            dialog.destroy()
        
        def on_cancel():
            cancel_callback()
            dialog.destroy()
        
        tk.Button(button_frame, text="Speichern", command=on_save, bg="green", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Abbrechen", command=on_cancel, bg="red", fg="white").pack(side="left", padx=5)
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        return dialog
    
    def create_project_management_dialog(
        self,
        project_list: List[str],
        current_project: str,
        add_project_callback: Callable,
        remove_project_callback: Callable,
        set_active_callback: Callable,
        close_callback: Callable
    ) -> None:
        """
        Create project management dialog.
        
        Args:
            project_list: List of available projects
            current_project: Currently active project
            add_project_callback: Function to call when adding project
            remove_project_callback: Function to call when removing project
            set_active_callback: Function to call when setting active project
            close_callback: Function to call when closing dialog
        """
        dialog = tk.Toplevel(self.parent)
        dialog.title("Project Management")
        center_window(dialog, 600, 500)
        dialog.resizable(True, True)
        
        # Header
        header_label = tk.Label(
            dialog, 
            text="📁 Project Management", 
            font=("Arial", 16, "bold"), 
            fg="#2c3e50"
        )
        header_label.pack(pady=10)
        
        # Current project display
        current_frame = tk.Frame(dialog, bg="#ecf0f1", relief="groove", bd=2)
        current_frame.pack(pady=5, padx=20, fill="x")
        
        tk.Label(
            current_frame,
            text=f"Aktuelles Projekt: {current_project}",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#27ae60"
        ).pack(pady=5)
        
        # Project list
        list_frame = tk.Frame(dialog)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        tk.Label(list_frame, text="Verfügbare Projekte:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill="both", expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        project_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=8)
        project_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=project_listbox.yview)
        
        # Load projects
        for i, project in enumerate(project_list):
            project_listbox.insert(tk.END, project)
            if project == current_project:
                project_listbox.selection_set(i)
        
        # New project input
        new_project_frame = tk.Frame(dialog)
        new_project_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(new_project_frame, text="Neues Projekt:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        new_project_var = tk.StringVar()
        new_project_entry = tk.Entry(new_project_frame, textvariable=new_project_var, width=50)
        new_project_entry.pack(pady=5, fill="x")
        
        # Button functions
        def add_project():
            new_project = new_project_var.get().strip()
            if new_project and new_project not in project_list:
                project_list.append(new_project)
                project_listbox.insert(tk.END, new_project)
                new_project_var.set("")
                add_project_callback(new_project)
                print(f"Project '{new_project}' added")
            elif new_project in project_list:
                messagebox.showwarning("Projekt existiert", f"Das Projekt '{new_project}' existiert bereits.")
        
        def remove_project():
            selected = project_listbox.curselection()
            if selected:
                index = selected[0]
                project_name = project_list[index]
                if project_name != "General":  # Prevent removing default project
                    result = messagebox.askyesno(
                        "Projekt entfernen",
                        f"Möchten Sie das Projekt '{project_name}' wirklich entfernen?"
                    )
                    if result:
                        project_list.remove(project_name)
                        project_listbox.delete(index)
                        remove_project_callback(project_name)
                        print(f"Project '{project_name}' removed")
                else:
                    messagebox.showwarning("Warnung", "Das Standard-Projekt 'General' kann nicht entfernt werden.")
        
        def set_active_project():
            selected = project_listbox.curselection()
            if selected:
                index = selected[0]
                project_name = project_list[index]
                set_active_callback(project_name)
                close_callback()
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Hinzufügen", command=add_project, bg="#27ae60", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="🗑️ Entfernen", command=remove_project, bg="#e74c3c", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="✓ Aktiv setzen", command=set_active_project, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Schließen", command=close_callback, bg="#95a5a6", fg="white").pack(side="left", padx=5)
        
        # Enter key for adding
        new_project_entry.bind("<Return>", lambda e: add_project())
        
        dialog.transient(self.parent)
        dialog.grab_set()
        
        return dialog
    
    def show_info_message(self, title: str, message: str) -> None:
        """Show information message dialog."""
        messagebox.showinfo(title, message)
    
    def show_error_message(self, title: str, message: str) -> None:
        """Show error message dialog."""
        messagebox.showerror(title, message)
    
    def show_warning_message(self, title: str, message: str) -> None:
        """Show warning message dialog."""
        messagebox.showwarning(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """
        Show yes/no question dialog.
        
        Returns:
            True if user clicked Yes, False otherwise
        """
        return messagebox.askyesno(title, message)


class OverlayDisplayService:
    """
    Service for managing overlay display updates and formatting.
    
    Centralizes overlay-specific display logic and calculations.
    """
    
    def __init__(self):
        """Initialize overlay display service."""
        pass
    
    def format_work_status_display(self, work_time, pause_time, remaining_time, is_overtime: bool) -> Dict[str, str]:
        """
        Format work status for display in overlay.
        
        Args:
            work_time: Current work time
            pause_time: Current pause time
            remaining_time: Remaining work time
            is_overtime: Whether in overtime
            
        Returns:
            Dictionary with formatted display strings
        """
        work_str = format_timedelta(work_time)
        pause_str = format_timedelta(pause_time)
        
        if is_overtime:
            remaining_str = f"💪 +{format_timedelta(-remaining_time)}"
        else:
            remaining_str = f"⏳ {format_timedelta(remaining_time)}" if remaining_time.total_seconds() > 0 else "🏠 Free Day"
        
        return {
            'work': f"🕐 {work_str}",
            'pause': f"☕ {pause_str}",
            'remaining': remaining_str
        }
    
    def format_status_display(self, is_working: bool, has_note: bool, pause_start: Optional[Any]) -> Dict[str, str]:
        """
        Format status display for overlay.
        
        Args:
            is_working: Whether currently working
            has_note: Whether current session has a note
            pause_start: Pause start time if in pause
            
        Returns:
            Dictionary with status text and color
        """
        if is_working:
            if has_note:
                return {'text': "⚡ Active (Task)", 'color': "#27ae60"}
            else:
                return {'text': "▶️ Working", 'color': "#27ae60"}
        elif pause_start:
            return {'text': "⏸️ Break", 'color': "#f39c12"}
        else:
            return {'text': "⏹️ Ready", 'color': "#95a5a6"}
