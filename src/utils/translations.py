"""
Translation Module for taskonaut

Provides translation utilities and text constants in English
"""

# English translations for common German strings
TRANSLATIONS = {
    # Time-related
    "Arbeitszeit": "Work Time",
    "Pausenzeit": "Break Time", 
    "Sollzeit": "Target Time",
    "Differenz": "Difference",
    "Dauer": "Duration",
    
    # Projects
    "Allgemein": "General",
    "Projekt": "Project",
    "Projekte": "Projects",
    "aktives_projekt": "active_project",
    "projekt_liste": "project_list",
    
    # Dates
    "Datum": "Date",
    "montag": "monday",
    "dienstag": "tuesday", 
    "mittwoch": "wednesday",
    "donnerstag": "thursday",
    "freitag": "friday",
    "samstag": "saturday",
    "sonntag": "sunday",
    
    # Excel sheets
    "Sessions": "Sessions",
    "Auswertung": "Evaluation",
    
    # Actions
    "Start": "Start",
    "Ende": "End", 
    "Stopp": "Stop",
    "Pause": "Break",
    "Notiz": "Note",
    
    # Files
    "arbeitszeiten.xlsx": "working_hours.xlsx",
    "excel_datei": "excel_file",
    "notiz_dialog": "note_dialog",
    
    # Config sections
    "arbeitszeiten": "work_hours",
    "pausenzeiten": "break_times",
    "projekte": "projects",
    
    # Config keys
    "min_pause_nach_stunden": "min_break_after_hours",
    "min_pause_dauer_minuten": "min_break_duration_minutes",
}

# UI Text constants in English
UI_TEXTS = {
    "work_started": "Work started at: {time}",
    "work_stopped": "Work stopped at: {time}",
    "break_started": "Break started at: {time}",
    "break_ended": "Break ended at: {time}",
    "project_switched": "Switched to project: {project}",
    "session_saved": "Session saved successfully",
    "config_loaded": "Configuration loaded successfully",
    "data_loaded": "Today's data loaded: {work_time} work, {break_time} break",
    "sessions_loaded": "{count} sessions loaded, current project: {project}",
    "error_saving": "Error saving configuration: {error}",
    "work_time_label_clicked": "🕐 Work time label clicked",
    "start_day": "  -> Start day",
    "stop_day": "  -> Stop day", 
    "pause_work": "  -> Pause work",
    "resume_work": "  -> Resume work",
    "switch_project": "  -> Switch project",
    "show_session_info": "  -> Show session info",
    "show_settings": "  -> Show settings",
    "quit_app": "  -> Quit application",
}

def translate_key(german_key: str) -> str:
    """Translate a German configuration key to English"""
    return TRANSLATIONS.get(german_key, german_key)

def get_ui_text(key: str, **kwargs) -> str:
    """Get UI text with formatting"""
    text = UI_TEXTS.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def translate_config_dict(config_dict: dict) -> dict:
    """Recursively translate German config keys to English"""
    if not isinstance(config_dict, dict):
        return config_dict
    
    translated = {}
    for key, value in config_dict.items():
        new_key = translate_key(key)
        if isinstance(value, dict):
            translated[new_key] = translate_config_dict(value)
        elif isinstance(value, list):
            # Translate project names
            if key == "projekt_liste":
                translated[new_key] = [translate_key(item) if isinstance(item, str) else item for item in value]
            else:
                translated[new_key] = value
        elif isinstance(value, str):
            translated[new_key] = translate_key(value)
        else:
            translated[new_key] = value
    
    return translated
