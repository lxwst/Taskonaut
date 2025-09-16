"""
Configuration Management Module

Handles loading, saving, and validation of application configuration.
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Loads configuration from file or creates default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = f.read()
                    if not config_data.strip():
                        raise ValueError("Config file is empty")
                    self.config = json.loads(config_data)
                
                # Validate required keys
                self._validate_config()
            else:
                self._create_default_config()
                
        except (FileNotFoundError, json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Config error: {e}. Creating default configuration.")
            self._create_default_config()
        except Exception as e:
            print(f"Unexpected error loading config: {e}")
            self._create_default_config()
    
    def save_config(self) -> None:
        """Saves current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            raise
    
    def save(self) -> None:
        """Alias for save_config for compatibility"""
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Returns complete configuration dictionary"""
        return self.config.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Gets configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Sets configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
    
    def _validate_config(self) -> None:
        """Validates configuration structure"""
        required_keys = ['work_hours', 'excel_file']
        for key in required_keys:
            if key not in self.config:
                raise KeyError(f"Required config key '{key}' missing")
    
    def _create_default_config(self) -> None:
        """Creates default configuration"""
        self.config = {
            "work_hours": {
                "monday": 8.0,
                "tuesday": 8.0,
                "wednesday": 8.0,
                "thursday": 8.0,
                "friday": 8.0,
                "saturday": 0.0,
                "sunday": 0.0
            },
            "break_times": {
                "min_break_after_hours": 6.0,
                "min_break_duration_minutes": 30
            },
            "excel_file": "working_hours.xlsx",
            "note_dialog": True,
            "overlay": {
                "enabled": True,
                "width": 200,
                "height": 120,
                "font_size": 12,
                "transparency": 0.9,
                "background_color": "#2c3e50",
                "text_color": "#ecf0f1"
            },
            "projects": {
                "active_project": "General",
                "project_list": [
                    "General",
                    "Project A - Web Development",
                    "Project B - Data Analysis", 
                    "Project C - Design",
                    "Administration",
                    "Meetings",
                    "Training"
                ]
            }
        }
        self.save_config()
    
    def get_target_hours_today(self) -> float:
        """Returns target work hours for today"""
        from datetime import datetime
        
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        today = datetime.now().weekday()
        return self.config['work_hours'][weekdays[today]]
    
    def get_target_hours_for_date(self, date_obj) -> float:
        """Returns target work hours for specific date"""
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        weekday = date_obj.weekday()
        return self.config['work_hours'][weekdays[weekday]]
