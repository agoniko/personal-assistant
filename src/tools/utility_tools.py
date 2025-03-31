"""
Utility tools for the assistant.
"""
from typing import Optional
from datetime import datetime, timedelta
import pytz
import re
import sys
import os

# Add parent directory to path if running as a script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.base import BaseTool, register_tool
import src.config as config

@register_tool
class GetCurrentTimeTool(BaseTool):
    """Tool for getting the current time."""
    
    name = "get_current_time"
    description = "Get the current time and date in the user's timezone"
    
    def execute(self, format: Optional[str] = None) -> str:
        """
        Get the current time and date.
        
        Args:
            format: Optional format string for the datetime (defaults to ISO format).
            
        Returns:
            The current time and date as a formatted string.
        """
        try:
            tz = pytz.timezone(config.TIMEZONE)
            now = datetime.now(tz)
            
            if format:
                return now.strftime(format)
            
            return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} {now.tzname()}"
        except Exception as e:
            return f"Error getting current time: {str(e)}"

@register_tool
class GetDateInfoTool(BaseTool):
    """Tool for getting information about a specific date."""
    
    name = "get_date_info"
    description = "Get information about a specific date like day of week, week number, etc."
    
    def execute(self, date: Optional[str] = None) -> str:
        """
        Get information about a date.
        
        Args:
            date: Date string in format YYYY-MM-DD (defaults to today).
            
        Returns:
            Information about the specified date.
        """
        try:
            tz = pytz.timezone(config.TIMEZONE)
            
            if date:
                dt = datetime.strptime(date, "%Y-%m-%d")
                dt = tz.localize(dt)
            else:
                dt = datetime.now(tz)
            
            return (
                f"Date: {dt.strftime('%Y-%m-%d')}\n"
                f"Day of week: {dt.strftime('%A')}\n"
                f"Week number: {dt.strftime('%U')}\n"
                f"Month: {dt.strftime('%B')}\n"
                f"Day of year: {dt.strftime('%j')}\n"
                f"Timezone: {dt.tzname()}"
            )
        except Exception as e:
            return f"Error getting date information: {str(e)}"

@register_tool
class CalculateDateDifferenceTool(BaseTool):
    """Tool for calculating the difference between two dates."""
    
    name = "calculate_date_difference"
    description = "Calculate the number of days, weeks, or months between two dates"
    
    def execute(self, start_date: str, end_date: str) -> str:
        """
        Calculate the difference between two dates.
        
        Args:
            start_date: Start date in format YYYY-MM-DD.
            end_date: End date in format YYYY-MM-DD.
            
        Returns:
            The difference between the dates in days, weeks, and months.
        """
        try:
            date_format = "%Y-%m-%d"
            start = datetime.strptime(start_date, date_format)
            end = datetime.strptime(end_date, date_format)
            
            # Calculate the difference
            diff = end - start
            days = diff.days
            
            # Calculate weeks and months approximately
            weeks = days // 7
            months = days // 30
            
            return (
                f"Difference between {start_date} and {end_date}:\n"
                f"Days: {days}\n"
                f"Weeks: {weeks}\n"
                f"Months (approximate): {months}"
            )
        except Exception as e:
            return f"Error calculating date difference: {str(e)}"

@register_tool
class GenerateDateRangeTool(BaseTool):
    """Tool for generating a range of dates."""
    
    name = "generate_date_range"
    description = "Generate a range of dates between start and end dates"
    
    def execute(
        self, 
        start_date: str, 
        end_date: str, 
        interval: str = "day",
        max_dates: int = 10
    ) -> str:
        """
        Generate a range of dates.
        
        Args:
            start_date: Start date in format YYYY-MM-DD.
            end_date: End date in format YYYY-MM-DD.
            interval: Interval between dates (day, week, month).
            max_dates: Maximum number of dates to generate.
            
        Returns:
            A list of dates in the specified range.
        """
        try:
            date_format = "%Y-%m-%d"
            start = datetime.strptime(start_date, date_format)
            end = datetime.strptime(end_date, date_format)
            
            if start > end:
                return "Error: Start date must be before end date."
            
            dates = []
            current = start
            
            # Set the delta based on the interval
            if interval.lower() == "day":
                delta = timedelta(days=1)
            elif interval.lower() == "week":
                delta = timedelta(weeks=1)
            elif interval.lower() == "month":
                # Approximate a month as 30 days
                delta = timedelta(days=30)
            else:
                return f"Error: Invalid interval '{interval}'. Use 'day', 'week', or 'month'."
            
            # Generate dates
            count = 0
            while current <= end and count < max_dates:
                dates.append(current.strftime(date_format))
                current += delta
                count += 1
            
            total_dates = len(dates)
            if current <= end:
                dates.append("...")
            
            return (
                f"Date range from {start_date} to {end_date} by {interval}:\n"
                f"{', '.join(dates)}\n"
                f"Generated {total_dates} dates" + 
                (f" (limited to {max_dates})" if current <= end else "")
            )
        except Exception as e:
            return f"Error generating date range: {str(e)}"

@register_tool
class ParseDateTool(BaseTool):
    """Tool for parsing dates from natural language."""
    
    name = "parse_date"
    description = "Convert a natural language date description into a formatted date"
    
    def execute(self, date_text: str, gmail_format: bool = False) -> str:
        """
        Parse a natural language date into a formatted date.
        
        Args:
            date_text: Natural language date description (e.g., "tomorrow", "next Monday").
            gmail_format: If True, returns date in Gmail API format (YYYY/MM/DD).
            
        Returns:
            The parsed date in YYYY-MM-DD format (or YYYY/MM/DD if gmail_format=True).
        """
        try:
            tz = pytz.timezone(config.TIMEZONE)
            now = datetime.now(tz)
            result_date = None
            
            # Common date patterns
            today_pattern = re.compile(r'\b(?:today|now)\b', re.IGNORECASE)
            tomorrow_pattern = re.compile(r'\btomorrow\b', re.IGNORECASE)
            yesterday_pattern = re.compile(r'\byesterday\b', re.IGNORECASE)
            next_week_pattern = re.compile(r'\bnext\s+week\b', re.IGNORECASE)
            next_month_pattern = re.compile(r'\bnext\s+month\b', re.IGNORECASE)
            next_day_pattern = re.compile(r'\bnext\s+(\w+day)\b', re.IGNORECASE)
            
            # Check patterns
            if today_pattern.search(date_text):
                result_date = now
            elif tomorrow_pattern.search(date_text):
                result_date = now + timedelta(days=1)
            elif yesterday_pattern.search(date_text):
                result_date = now - timedelta(days=1)
            elif next_week_pattern.search(date_text):
                result_date = now + timedelta(weeks=1)
            elif next_month_pattern.search(date_text):
                # Approximate next month
                result_date = now + timedelta(days=30)
            elif next_day_match := next_day_pattern.search(date_text):
                day_name = next_day_match.group(1).lower()
                days = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                if day_name in days:
                    target_day = days[day_name]
                    days_ahead = (target_day - now.weekday()) % 7
                    if days_ahead == 0:  # It's the same day, so get next week
                        days_ahead = 7
                    result_date = now + timedelta(days=days_ahead)
            
            if result_date:
                # Format based on requirement
                if gmail_format:
                    formatted_date = result_date.strftime('%Y/%m/%d')
                else:
                    formatted_date = result_date.strftime('%Y-%m-%d')
                
                day_name = result_date.strftime('%A')
                
                response = f"'{date_text}' is {formatted_date} ({day_name})"
                if gmail_format:
                    response += f"\nFor Gmail API use: {formatted_date}"
                return response
            else:
                return f"Could not parse '{date_text}'. Please provide a date in YYYY-MM-DD format or a clearer description."
        except Exception as e:
            return f"Error parsing date: {str(e)}"

@register_tool
class GetYesterdayDateTool(BaseTool):
    """Tool specifically for getting yesterday's date in Gmail format."""
    
    name = "get_yesterday_date"
    description = "Get yesterday's date in Gmail format (YYYY/MM/DD)"
    
    def execute(self) -> str:
        """
        Get yesterday's date in Gmail API format.
        
        Returns:
            Yesterday's date in YYYY/MM/DD format for Gmail API.
        """
        try:
            tz = pytz.timezone(config.TIMEZONE)
            now = datetime.now(tz)
            yesterday = now - timedelta(days=1)
            
            # Gmail API uses YYYY/MM/DD format
            gmail_format = yesterday.strftime('%Y/%m/%d')
            
            return gmail_format
        except Exception as e:
            return f"Error getting yesterday's date: {str(e)}" 