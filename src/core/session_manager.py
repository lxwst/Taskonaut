"""
Session Management Module

Handles work sessions, time tracking, and session persistence.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils.time_utils import format_timedelta


class WorkSession:
    """Represents a single work session"""
    
    def __init__(self, start: datetime, end: Optional[datetime] = None, 
                 duration: Optional[timedelta] = None, note: str = "", 
                 project: str = "", task: str = ""):
        self.start = start
        self.end = end
        self.duration = duration
        self.note = note
        self.project = project
        self.task = task  # New task field
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts session to dictionary"""
        return {
            'start': self.start,
            'end': self.end,
            'duration': self.duration,
            'note': self.note,
            'project': self.project,
            'task': self.task
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkSession':
        """Creates session from dictionary"""
        return cls(
            start=data['start'],
            end=data.get('end'),
            duration=data.get('duration'),
            note=data.get('note', ''),
            project=data.get('project', ''),
            task=data.get('task', '')
        )


class SessionManager:
    """Manages work sessions and time tracking - CENTRALIZED WITH EXCEL INTEGRATION"""
    
    def __init__(self, excel_manager=None):
        # Core session state
        self.current_session: Optional[WorkSession] = None
        self.sessions: List[WorkSession] = []
        self.total_work_time = timedelta()
        self.total_pause_time = timedelta()
        self.pause_start: Optional[datetime] = None
        self.is_working = False
        self.unsaved_changes = False
        # Add new field for current session task
        self.current_session_task = ""
        
        # Current session state
        self.current_session_note = ""
        self.current_session_project = ""
        
        # Excel integration
        self.excel_manager = excel_manager
        
        # Load existing sessions if excel_manager provided
        if self.excel_manager:
            self.load_sessions_from_excel()
    
    def load_sessions_from_excel(self) -> None:
        """
        ZENTRALE METHODE: Lädt Sessions aus Excel und initialisiert SessionManager
        """
        if not self.excel_manager:
            print("⚠️ No ExcelManager provided - cannot load sessions")
            return
        
        try:
            print("📖 SessionManager: Loading sessions from Excel...")
            all_sessions = self.excel_manager.load_sessions()
            
            # Filter today's sessions
            today = datetime.now().date()
            today_sessions = [s for s in all_sessions if s.start.date() == today]
            
            print(f"📊 Found {len(all_sessions)} total sessions, {len(today_sessions)} for today")
            
            # Reset current state
            self.sessions = []
            self.total_work_time = timedelta()
            self.total_pause_time = timedelta()
            self.current_session = None
            self.is_working = False
            
            # Process today's sessions
            incomplete_session = None
            for session in today_sessions:
                if session.end is None:
                    # Found incomplete session
                    incomplete_session = session
                    print(f"🔄 Found incomplete session: {session.start.strftime('%H:%M')} - {session.project}")
                else:
                    # Complete session
                    self.sessions.append(session)
                    
                    # Calculate work and break time separately
                    session_duration = session.end - session.start
                    if session.project == 'BREAK':
                        self.total_pause_time += session_duration
                        print(f"☕ Break session loaded: {session.start.strftime('%H:%M')}-{session.end.strftime('%H:%M')} ({session_duration})")
                    else:
                        self.total_work_time += session_duration
                        print(f"🔨 Work session loaded: {session.start.strftime('%H:%M')}-{session.end.strftime('%H:%M')} ({session_duration})")
            
            # Calculate pause times between sessions
            self._calculate_pause_times()
            
            # Handle incomplete session
            if incomplete_session:
                self.current_session = incomplete_session
                self.current_session_note = incomplete_session.note
                self.current_session_project = incomplete_session.project
                self.is_working = True
                self.recovered_session = True
                self.unsaved_changes = True
                print(f"✅ Recovered incomplete session from {incomplete_session.start.strftime('%H:%M')}")
            
            print(f"✅ SessionManager initialized: {len(self.sessions)} sessions, working: {self.is_working}")
            
        except Exception as e:
            print(f"❌ Error loading sessions from Excel: {e}")
    
    # Removed legacy enhanced export method (handled directly by ExcelReportManager)

    def save_sessions_to_excel(self) -> bool:
        """
        ZENTRALE METHODE: Speichert alle Sessions über ExcelManager
        """
        if not self.excel_manager:
            print("⚠️ No ExcelManager provided - cannot save sessions")
            return False
        
        try:
            print("💾 SessionManager: Saving sessions to Excel...")
            
            # Get all sessions including current if completed
            all_sessions = self.sessions.copy()
            
            # Add current session if it's completed
            if self.current_session and self.current_session.end:
                all_sessions.append(self.current_session)
            
            # Save via ExcelManager using write_sessions (preserves old data)
            success = self.excel_manager.write_sessions(
                all_sessions, 
                self.total_work_time, 
                self.total_pause_time, 
                8.0  # Default target hours
            )
            
            if success:
                self.unsaved_changes = False
                print(f"✅ SessionManager: Saved {len(all_sessions)} sessions")
            else:
                print("❌ SessionManager: Failed to save sessions")
                
            return success
            
        except Exception as e:
            print(f"❌ Error saving sessions to Excel: {e}")
            return False
    
    def _calculate_pause_times(self) -> None:
        """Calculate pause times between sessions - only if no explicit break sessions exist"""
        if len(self.sessions) <= 1:
            return
        
        # Check if we have explicit break sessions
        has_break_sessions = any(session.project == 'BREAK' for session in self.sessions)
        
        if has_break_sessions:
            # Don't calculate pause times - use explicit break sessions
            print("📊 Using explicit break sessions instead of calculated pause times")
            return
        
        # Sort sessions by start time (only work sessions)
        work_sessions = [s for s in self.sessions if s.project != 'BREAK']
        sorted_sessions = sorted(work_sessions, key=lambda s: s.start)
        
        pause_time = timedelta()
        for i in range(len(sorted_sessions) - 1):
            current_end = sorted_sessions[i].end
            next_start = sorted_sessions[i + 1].start
            
            if current_end and next_start > current_end:
                pause_time += (next_start - current_end)
        
        self.total_pause_time = pause_time
        print(f"📊 Calculated pause time between work sessions: {pause_time}")
    
    def get_today_sessions(self) -> List[WorkSession]:
        """Returns all sessions for today"""
        today = datetime.now().date()
        return [s for s in self.sessions if s.start.date() == today]
    
    def get_current_session_duration(self) -> str:
        """Returns formatted duration of current session"""
        if not self.current_session:
            return "00:00:00"
        
        duration = datetime.now() - self.current_session.start
        return format_timedelta(duration)
    
    def recover_session_from_excel(self, incomplete_session: Dict[str, Any]) -> bool:
        """
        Recovers an incomplete session from Excel data
        
        Args:
            incomplete_session: Dictionary with session data from Excel
            
        Returns:
            True if session was successfully recovered
        """
        try:
            start_time = incomplete_session['start_time']
            project = incomplete_session.get('project', 'General')
            note = incomplete_session.get('note', '')
            
            # Create and start the recovered session
            self.current_session = WorkSession(start=start_time, project=project, note=note)
            self.current_session_note = note
            self.current_session_project = project
            self.is_working = True
            self.recovered_session = True
            self.unsaved_changes = True
            
            print(f"🔄 Session recovered from Excel:")
            print(f"   Start time: {start_time.strftime('%H:%M')}")
            print(f"   Project: {project}")
            print(f"   Note: '{note}'")
            print(f"   Running for: {self.get_current_session_duration()}")
            
            return True
            
        except Exception as e:
            print(f"Error recovering session: {e}")
            return False
    
    def get_recovery_status(self) -> str:
        """Returns status string if session was recovered"""
        if self.recovered_session and self.is_working:
            elapsed = self.get_current_session_duration()
            return f"Recovered session • Running for {elapsed}"
        return ""
    
    def start_session(self, project: str = "", note: str = "", task: str = "") -> None:
        """Starts a new work session"""
        if self.is_working:
            raise ValueError("Session already running")
        
        now = datetime.now()
        
        # End pause if active
        if self.pause_start:
            pause_duration = now - self.pause_start
            self.total_pause_time += pause_duration
            self.pause_start = None
        
        # Start new session
        self.current_session = WorkSession(start=now, project=project, note=note, task=task)
        self.current_session_note = note
        self.current_session_project = project
        self.current_session_task = task
        self.is_working = True
        self.unsaved_changes = True
        
        print(f"Session started at: {now.strftime('%H:%M')}")
        print(f"Project: {project}")
        print(f"Note: '{note}'")
    
    def stop_session(self) -> Optional[WorkSession]:
        """Stops current session and returns it"""
        if not self.is_working or not self.current_session:
            print("No active session to stop")
            return None
        
        now = datetime.now()
        
        # Complete current session
        self.current_session.end = now
        self.current_session.duration = now - self.current_session.start
        self.current_session.note = self.current_session_note or "Session ended"
        self.current_session.project = self.current_session_project or "Allgemein"
        
        # Add to sessions list
        self.sessions.append(self.current_session)
        self.total_work_time += self.current_session.duration
        
        print(f"Session stopped at: {now.strftime('%H:%M')}")
        print(f"Duration: {format_timedelta(self.current_session.duration)}")
        print(f"Project: {self.current_session.project}")
        print(f"Note: '{self.current_session.note}'")
        
        # Reset session state
        completed_session = self.current_session
        self.current_session = None
        self.current_session_note = ""
        self.current_session_project = ""
        self.is_working = False
        self.pause_start = now
        self.unsaved_changes = True
        
        # Auto-save to Excel if manager available
        if self.excel_manager:
            self.save_sessions_to_excel()
        
        return completed_session
    
    def switch_project(self, new_project: str) -> Optional[WorkSession]:
        """Switches project, saving current session if active"""
        if self.is_working and self.current_session:
            # Stop current session and start new one
            completed_session = self.stop_session()
            self.start_session(project=new_project, note="")
            return completed_session
        else:
            # Just update project for next session
            self.current_session_project = new_project
            return None
    
    def update_session_note(self, note: str) -> None:
        """Updates current session note"""
        self.current_session_note = note
        if self.current_session:
            self.current_session.note = note
    
    def get_current_work_time(self) -> timedelta:
        """Returns current total work time including active session"""
        current_work = self.total_work_time
        
        if self.is_working and self.current_session:
            current_work += datetime.now() - self.current_session.start
        
        return current_work
    
    def get_current_pause_time(self) -> timedelta:
        """Returns current total pause time including active pause"""
        current_pause = self.total_pause_time
        
        if self.pause_start and not self.is_working:
            current_pause += datetime.now() - self.pause_start
        
        return current_pause
    
    def has_unsaved_data(self) -> bool:
        """Checks if there are unsaved changes"""
        return self.unsaved_changes  # Simple flag-based approach
    
    def end_work_day(self) -> bool:
        """Ends the work day by stopping any active session and saving all data"""
        try:
            print("🏁 Ending work day...")
            
            # Stop any active session first
            if self.is_working:
                self.stop_session()
            
            # End any active pause (day is over, no more pause time)
            if self.pause_start:
                pause_duration = datetime.now() - self.pause_start
                self.total_pause_time += pause_duration
                self.pause_start = None
                print(f"📊 Final pause duration added: {pause_duration}")
            
            # Save all data
            success = self.save_sessions_to_excel()
            
            if success:
                # Mark day as completed (no more unsaved changes)
                self.unsaved_changes = False
                print("✅ Work day ended successfully - no more timers running")
                return True
            else:
                print("❌ Failed to end work day - save failed")
                return False
                
        except Exception as e:
            print(f"❌ Error ending work day: {e}")
            return False

    def update_sessions(self, sessions: List[WorkSession]) -> None:
        """Updates the session list with provided sessions"""
        self.sessions = sessions.copy()
        self.unsaved_changes = True
        print(f"✅ SessionManager: Updated with {len(sessions)} sessions")
        
    def delete_session(self, index: int) -> bool:
        """Deletes a session at the specified index"""
        try:
            if 0 <= index < len(self.sessions):
                deleted_session = self.sessions.pop(index)
                self.unsaved_changes = True
                print(f"🗑️ SessionManager: Deleted session at index {index} - {deleted_session.project}")
                return True
            else:
                print(f"❌ SessionManager: Invalid index {index} for deletion (sessions: {len(self.sessions)})")
                return False
        except Exception as e:
            print(f"❌ SessionManager: Error deleting session at index {index}: {e}")
            return False
        
    def reset_day(self) -> None:
        """Resets all times for a new day"""
        self.current_session = None
        self.sessions = []
        self.total_work_time = timedelta()
        self.total_pause_time = timedelta()
        self.pause_start = None
        self.is_working = False
        self.unsaved_changes = False
        self.current_session_note = ""
        self.current_session_project = ""
        print("Day reset - all times cleared")
    
    def finish_current_session(self) -> None:
        """Finishes current session without starting pause"""
        if self.is_working and self.current_session:
            now = datetime.now()
            self.current_session.end = now
            self.current_session.duration = now - self.current_session.start
            self.current_session.note = self.current_session_note or '[Auto-finished]'
            self.current_session.project = self.current_session_project or "Allgemein"
            
            self.sessions.append(self.current_session)
            self.total_work_time += self.current_session.duration
            self.is_working = False
            
            # Reset session variables
            self.current_session = None
            self.current_session_note = ""
            self.current_session_project = ""
            
            # Auto-save to Excel if manager available
            if self.excel_manager:
                self.save_sessions_to_excel()
    
    def update_session(self, session_index: int, start: datetime, end: datetime, project: str, note: str) -> bool:
        """
        Updates a specific session and saves to Excel
        
        Args:
            session_index: Index of session to update
            start: New start time
            end: New end time  
            project: New project
            note: New note
            
        Returns:
            True if update successful
        """
        try:
            if 0 <= session_index < len(self.sessions):
                session = self.sessions[session_index]
                session.start = start
                session.end = end
                session.project = project
                session.note = note
                session.duration = end - start if end else None
                
                # Recalculate totals
                self._recalculate_totals()
                
                # Auto-save to Excel if manager available
                if self.excel_manager:
                    return self.save_sessions_to_excel()
                    
                return True
            return False
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def _recalculate_totals(self) -> None:
        """Recalculates total work and pause times"""
        self.total_work_time = timedelta()
        self.total_pause_time = timedelta()
        
        for session in self.sessions:
            if session.end:
                session_duration = session.end - session.start
                if session.project == 'BREAK':
                    self.total_pause_time += session_duration
                else:
                    self.total_work_time += session_duration
        
        # Note: We don't call _calculate_pause_times() here as it would override 
        # the explicit break sessions with calculated pause times
