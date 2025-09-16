"""
Time utility functions

Provides helper functions for time formatting and calculations.
"""

from datetime import datetime, timedelta
from typing import Optional


def format_timedelta(td: timedelta) -> str:
    """
    Formats a timedelta as HH:MM:SS string
    
    Args:
        td: The timedelta to format
        
    Returns:
        Formatted time string (e.g., "08:30:45")
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_time_string(time_str: str) -> Optional[timedelta]:
    """
    Parses a time string (HH:MM:SS or HH:MM) into a timedelta
    
    Args:
        time_str: Time string to parse
        
    Returns:
        Timedelta object or None if parsing fails
    """
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            hours, minutes = map(int, parts)
            seconds = 0
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
        else:
            return None
        
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except (ValueError, TypeError):
        return None


def time_difference(start: datetime, end: datetime) -> timedelta:
    """
    Calculates the difference between two datetime objects
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Time difference as timedelta
    """
    return end - start


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """
    Checks if two datetime objects are on the same day
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        True if same day, False otherwise
    """
    return dt1.date() == dt2.date()


def get_day_start(dt: datetime) -> datetime:
    """
    Gets the start of the day (00:00:00) for a given datetime
    
    Args:
        dt: Datetime object
        
    Returns:
        Datetime at start of day
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_day_end(dt: datetime) -> datetime:
    """
    Gets the end of the day (23:59:59) for a given datetime
    
    Args:
        dt: Datetime object
        
    Returns:
        Datetime at end of day
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def format_datetime_for_display(dt: datetime) -> str:
    """
    Formats datetime for user display
    
    Args:
        dt: Datetime to format
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime("%d.%m.%Y %H:%M")


def format_time_for_display(dt: datetime) -> str:
    """
    Formats time portion for user display
    
    Args:
        dt: Datetime to format
        
    Returns:
        Formatted time string (HH:MM)
    """
    return dt.strftime("%H:%M")


def calculate_remaining_time(target_hours: float, current_time: timedelta) -> timedelta:
    """
    Calculates remaining work time based on target hours
    
    Args:
        target_hours: Target work hours for the day
        current_time: Current work time as timedelta
        
    Returns:
        Remaining time as timedelta (can be negative if overtime)
    """
    target_time = timedelta(hours=target_hours)
    return target_time - current_time
