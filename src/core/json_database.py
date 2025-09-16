"""
JSON Database Manager

Handles all data persistence using JSON files as the primary database.
Excel files are generated as exports from JSON data.
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid


@dataclass
class TimeSession:
    """Represents a time tracking session"""
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    project: str
    task: str
    duration_seconds: int
    is_active: bool
    session_type: str  # 'work' or 'break'
    note: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'project': self.project,
            'task': self.task,
            'duration_seconds': self.duration_seconds,
            'is_active': self.is_active,
            'session_type': self.session_type,
            'note': self.note
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSession':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            id=data['id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data['end_time'] else None,
            project=data['project'],
            task=data['task'],
            duration_seconds=data['duration_seconds'],
            is_active=data['is_active'],
            session_type=data['session_type'],
            note=data.get('note', '')
        )


class JsonDatabase:
    """JSON-based database for time tracking application"""
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        # projects.json deprecated – projects now embedded in config.json under 'projects_data'
        self.projects_file = os.path.join(data_dir, "projects.json")  # kept for migration
        self.config_file = os.path.join(data_dir, "config.json")
        
        # In-memory data
        self.sessions: List[TimeSession] = []
        self.projects_data: Dict[str, Any] = {}
        self.config_data: Dict[str, Any] = {}
        
        # Load existing data
        self.load_all_data()
    
    def load_all_data(self):
        """Load all data from JSON files"""
        self.load_sessions()
        self.load_config()
        # After config loaded, if embedded projects exist, use them; else migrate old file if present
        self._post_load_projects_migration()
    
    def load_sessions(self):
        """Load sessions from JSON file"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                    self.sessions = [TimeSession.from_dict(s) for s in sessions_data]
                print(f"✅ Loaded {len(self.sessions)} sessions from JSON")
            else:
                self.sessions = []
                print("📝 No existing sessions file, starting fresh")
        except Exception as e:
            print(f"❌ Error loading sessions: {e}")
            self.sessions = []
    
    def save_sessions(self):
        """Save sessions to JSON file"""
        try:
            sessions_data = [session.to_dict() for session in self.sessions]
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.sessions)} sessions to JSON")
            return True
        except Exception as e:
            print(f"❌ Error saving sessions: {e}")
            return False
    
    def load_projects(self):  # legacy compatibility: now reads from config if possible
        if not self.projects_data:
            embedded = self.config_data.get('projects_data') or self.config_data.get('projects')
            if isinstance(embedded, dict):
                # Normalize if old 'projects' structure used
                if 'projects' in embedded and 'active_project' in embedded:
                    self.projects_data = embedded
                    print("✅ Loaded projects data from embedded config")
                else:
                    # Fallback default structure
                    self.projects_data = {
                        'active_project': 'General',
                        'active_task': 'Daily Work',
                        'projects': embedded if isinstance(embedded, dict) else {},
                        'recent_combinations': []
                    }
                    print("✅ Constructed projects data from simplified config section")
            elif os.path.exists(self.projects_file):
                try:
                    with open(self.projects_file, 'r', encoding='utf-8') as f:
                        self.projects_data = json.load(f)
                    print("✅ Migrated legacy projects.json data")
                except Exception as e:
                    print(f"❌ Failed loading legacy projects.json: {e}")
        return self.projects_data

    def save_projects(self):  # write back into config.json
        try:
            self.config_data['projects_data'] = self.projects_data
            self.save_config()
            return True
        except Exception as e:
            print(f"❌ Error saving embedded projects: {e}")
            return False

    def _post_load_projects_migration(self):
        # If separate projects.json exists and not yet embedded, migrate then optionally rename old file
        if 'projects_data' in self.config_data:
            self.projects_data = self.config_data['projects_data']
            return
        # Attempt legacy load for migration
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    legacy = json.load(f)
                if isinstance(legacy, dict) and 'projects' in legacy:
                    self.projects_data = legacy
                    self.config_data['projects_data'] = legacy
                    self.save_config()
                    print("� Migrated legacy projects.json into config.json (projects_data)")
            except Exception as e:
                print(f"⚠️ Migration of projects.json failed: {e}")
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            'overlay_settings': {
                'position': {'x': 100, 'y': 100},
                'transparency': 0.9,
                'font_size': 11,
                'always_on_top': True,
                'show_seconds': False
            },
            'work_settings': {
                'target_hours_per_day': 8.0,
                'auto_break_after_minutes': 60,
                'break_reminder_enabled': True
            },
            'excel_export': {
                'filename': 'working_hours.xlsx',
                'auto_export_daily': True
            },
            # New default for auto split threshold (minutes)
            'auto_split_minutes': 5
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                # Inject default auto_split_minutes if missing
                if 'auto_split_minutes' not in self.config_data:
                    self.config_data['auto_split_minutes'] = default_config['auto_split_minutes']
                print("✅ Loaded configuration from JSON")
            else:
                self.config_data = default_config
                self.save_config()
                print("📝 Created default configuration")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            self.config_data = default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            print("💾 Saved configuration to JSON")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    # Session Management Methods
    def create_session(self, project: str, task: str, session_type: str = 'work') -> TimeSession:
        """Create a new session"""
        session = TimeSession(
            id=str(uuid.uuid4()),
            start_time=datetime.now(),
            end_time=None,
            project=project,
            task=task,
            duration_seconds=0,
            is_active=True,
            session_type=session_type
        )
        self.sessions.append(session)
        self.update_recent_combination(project, task)
        print(f"🎬 Created new {session_type} session: {project} - {task}")
        return session
    
    def get_active_session(self) -> Optional[TimeSession]:
        """Get the currently active session"""
        for session in self.sessions:
            if session.is_active:
                return session
        return None
    
    def stop_active_session(self) -> Optional[TimeSession]:
        """Stop the currently active session"""
        active = self.get_active_session()
        if active:
            active.end_time = datetime.now()
            active.is_active = False
            active.duration_seconds = int((active.end_time - active.start_time).total_seconds())
            print(f"⏹️ Stopped session: {active.project} - {active.task} ({active.duration_seconds}s)")
            return active
        return None
    
    def get_today_sessions(self, session_type: Optional[str] = None) -> List[TimeSession]:
        """Get today's sessions, optionally filtered by type"""
        today = date.today()
        today_sessions = []
        
        for session in self.sessions:
            session_date = session.start_time.date()
            if session_date == today:
                if session_type is None or session.session_type == session_type:
                    today_sessions.append(session)
        
        return sorted(today_sessions, key=lambda s: s.start_time)
    
    def get_today_work_seconds(self) -> int:
        """Get total work seconds for today (excluding breaks)"""
        work_sessions = self.get_today_sessions('work')
        total_seconds = 0
        
        for session in work_sessions:
            if session.end_time:
                total_seconds += session.duration_seconds
            elif session.is_active:
                # Include current active time
                current_duration = int((datetime.now() - session.start_time).total_seconds())
                total_seconds += current_duration
        
        return total_seconds
    
    def get_today_break_seconds(self) -> int:
        """Get total break seconds for today"""
        today = date.today()
        total_seconds = 0
        
        # Count ALL break sessions for today - both session_type='break' AND project='BREAK'
        for session in self.sessions:
            session_date = session.start_time.date()
            if (session_date == today and 
                (session.session_type == 'break' or session.project == 'BREAK')):
                
                if session.end_time:
                    total_seconds += session.duration_seconds
                elif session.is_active:
                    current_duration = int((datetime.now() - session.start_time).total_seconds())
                    total_seconds += current_duration
        
        return total_seconds
    
    def get_today_required_work_seconds(self) -> int:
        """Get required work hours for today from config"""
        try:
            today = datetime.now()
            day_name = today.strftime('%A').lower()  # monday, tuesday, etc.
            
            # Get work hours from config
            work_hours = self.config_data.get('work_hours', {})
            daily_hours = work_hours.get(day_name, 8.0)  # Default to 8 hours
            
            # Convert hours to seconds
            return int(daily_hours * 3600)
        except Exception as e:
            print(f"Error getting required work hours: {e}")
            return 8 * 3600  # Default to 8 hours
    
    def update_recent_combination(self, project: str, task: str):
        """Update recent project-task combinations"""
        combination = f"{project} - {task}"
        recent = self.projects_data.get('recent_combinations', [])
        
        # Remove if already exists
        if combination in recent:
            recent.remove(combination)
        
        # Add to beginning
        recent.insert(0, combination)
        
        # Keep only last 10
        self.projects_data['recent_combinations'] = recent[:10]
    
    def get_recent_combinations(self) -> List[str]:
        """Get recent project-task combinations"""
        return self.projects_data.get('recent_combinations', [])
    
    def get_projects(self) -> Dict[str, List[str]]:
        """Get projects and their tasks"""
        return self.projects_data.get('projects', {})
    
    def get_active_project_task(self) -> tuple[str, str]:
        """Get currently active project and task"""
        return (
            self.projects_data.get('active_project', 'General'),
            self.projects_data.get('active_task', 'Daily Work')
        )
    
    def set_active_project_task(self, project: str, task: str):
        """Set active project and task"""
        self.projects_data['active_project'] = project
        self.projects_data['active_task'] = task
        self.update_recent_combination(project, task)
        self.save_projects()
    
    # Utility methods
    def format_seconds(self, seconds: int) -> str:
        """Format seconds as HH:MM or HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if self.config_data.get('overlay_settings', {}).get('show_seconds', False):
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}"
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Remove sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.sessions)
        
        self.sessions = [s for s in self.sessions if s.start_time >= cutoff_date]
        
        removed_count = original_count - len(self.sessions)
        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} old sessions")
            return True
        return False
    
    # Project Management Methods
    def get_available_projects(self):
        """Get list of available projects from database"""
        try:
            if 'projects' in self.projects_data:
                return list(self.projects_data['projects'].keys())
            else:
                # Fallback: get unique projects from sessions
                projects = set()
                for session in self.sessions:
                    if session.project and session.project != 'BREAK':
                        projects.add(session.project)
                return sorted(list(projects))
        except Exception as e:
            print(f"Error getting available projects: {e}")
            return ['General', 'Web Development', 'Documentation']
    
    def get_tasks_for_project(self, project):
        """Get available tasks for a specific project"""
        try:
            if ('projects' in self.projects_data and 
                project in self.projects_data['projects']):
                return self.projects_data['projects'][project]
            else:
                # Fallback: get tasks from sessions with this project
                tasks = set()
                for session in self.sessions:
                    if session.project == project and session.task:
                        tasks.add(session.task)
                return sorted(list(tasks)) if tasks else ['Daily Work']
        except Exception as e:
            print(f"Error getting tasks for project {project}: {e}")
            return ['Daily Work']
    
    def add_new_project(self, project_name, initial_tasks=None):
        """Add a new project to the database"""
        try:
            if initial_tasks is None:
                initial_tasks = ['Daily Work']
            
            if 'projects' not in self.projects_data:
                self.projects_data['projects'] = {}
            
            self.projects_data['projects'][project_name] = initial_tasks
            self.save_projects()
            
            print(f"➕ Added new project: {project_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding new project: {e}")
            return False
    
    def add_task_to_project(self, project_name, task_name):
        """Add a new task to an existing project"""
        try:
            if ('projects' in self.projects_data and 
                project_name in self.projects_data['projects']):
                
                if task_name not in self.projects_data['projects'][project_name]:
                    self.projects_data['projects'][project_name].append(task_name)
                    self.save_projects()
                    print(f"➕ Added new task '{task_name}' to project '{project_name}'")
                    return True
            return False
            
        except Exception as e:
            print(f"❌ Error adding task to project: {e}")
            return False
    
    # Session Management Methods for Session Editor
    def add_session(self, start_time: datetime, end_time: datetime = None, 
                   project: str = "General", task: str = "Daily Work", 
                   session_type: str = "work", note: str = ""):
        """Add a new session to the database"""
        try:
            # Generate unique ID
            session_id = f"session_{int(datetime.now().timestamp() * 1000)}"
            
            # Calculate duration if end time provided
            duration_seconds = 0
            is_active = False
            
            if end_time:
                duration_seconds = int((end_time - start_time).total_seconds())
            else:
                is_active = True
                end_time = None
            
            # Create new session
            new_session = TimeSession(
                id=session_id,
                start_time=start_time,
                end_time=end_time,
                project=project,
                task=task,
                duration_seconds=duration_seconds,
                is_active=is_active,
                session_type=session_type,
                note=note
            )
            
            self.sessions.append(new_session)
            print(f"➕ Added new session: {project} - {task} ({session_type})")
            return new_session
            
        except Exception as e:
            print(f"❌ Error adding session: {e}")
            return None
    
    def update_session(self, session: TimeSession):
        """Update an existing session in the database"""
        try:
            # Find the session in our list
            for i, existing_session in enumerate(self.sessions):
                if existing_session.id == session.id:
                    # Update the session
                    self.sessions[i] = session
                    print(f"✏️ Updated session: {session.project} - {session.task}")
                    return True
            
            print(f"⚠️ Session with ID {session.id} not found for update")
            return False
            
        except Exception as e:
            print(f"❌ Error updating session: {e}")
            return False
    
    def remove_session(self, session_id: str):
        """Remove a session from the database"""
        try:
            # Find and remove the session
            for i, session in enumerate(self.sessions):
                if session.id == session_id:
                    removed_session = self.sessions.pop(i)
                    print(f"🗑️ Removed session: {removed_session.project} - {removed_session.task}")
                    return True
            
            print(f"⚠️ Session with ID {session_id} not found for removal")
            return False
            
        except Exception as e:
            print(f"❌ Error removing session: {e}")
            return False
