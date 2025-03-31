"""
Calendar-related tools for interacting with Google Calendar.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pytz
from googleapiclient.discovery import build
import sys
import os

# Add parent directory to path if running as a script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.base import BaseTool, register_tool
from src.google_authenticator import GoogleAuthenticator
import src.config as config

class CalendarClient:
    """Handles interaction with the Google Calendar API."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CalendarClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the calendar client."""
        self.authenticator = GoogleAuthenticator()
        self.service = build('calendar', 'v3', credentials=self.authenticator.creds)
    
    def format_event(self, event: Dict[str, Any]) -> str:
        """Format an event dictionary into a readable string."""
        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No start time'))
        end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date', 'No end time'))
        summary = event.get('summary', 'No title')
        location = event.get('location', 'No location')
        description = event.get('description', 'No description')
        event_id = event.get('id', 'No ID')
        
        return (
            f"Event: {summary}\n"
            f"ID: {event_id}\n"
            f"Location: {location}\n"
            f"Start: {start}\n"
            f"End: {end}\n"
            f"Description: {description}\n"
        )
    
    def format_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """Format a list of event dictionaries into readable strings."""
        return [self.format_event(event) for event in events]

@register_tool
class AddEventTool(BaseTool):
    """Tool for adding an event to Google Calendar."""
    
    name = "add_calendar_event"
    description = "Add an event to the user's Google Calendar"
    
    def execute(
        self,
        summary: str,
        location: str,
        description: str,
        start_time: str,
        end_time: str,
    ) -> str:
        """
        Add an event to Google Calendar.
        
        Args:
            summary: The title of the event.
            location: The location of the event.
            description: A description of the event.
            start_time: The event's start time in ISO 8601 format (YYYY-MM-DDTHH:MM).
            end_time: The event's end time in ISO 8601 format (YYYY-MM-DDTHH:MM).
            
        Returns:
            A confirmation message with the event details.
        """
        try:
            client = CalendarClient()
            
            # Ensure times have timezone information
            tz = pytz.timezone(config.TIMEZONE)
            
            if not start_time.endswith('Z') and '+' not in start_time:
                dt = datetime.strptime(start_time, config.DATE_FORMAT)
                start_time = tz.localize(dt).isoformat()
            
            if not end_time.endswith('Z') and '+' not in end_time:
                dt = datetime.strptime(end_time, config.DATE_FORMAT)
                end_time = tz.localize(dt).isoformat()
            
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': config.TIMEZONE,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': config.TIMEZONE,
                },
            }
            
            created_event = client.service.events().insert(
                calendarId=config.CALENDAR_ID, 
                body=event
            ).execute()
            
            return (
                f"Event created successfully!\n"
                f"Event: {summary}\n"
                f"When: {start_time} to {end_time}\n"
                f"Link: {created_event.get('htmlLink')}"
            )
        except Exception as e:
            return f"Error adding event: {str(e)}"

@register_tool
class GetEventsByTimeTool(BaseTool):
    """Tool for retrieving events within a time range."""
    
    name = "get_calendar_events_by_time"
    description = "Get events from the user's Google Calendar within a specified time range"
    
    def execute(
        self,
        start_time: str,
        end_time: str,
        max_results: int = config.MAX_CALENDAR_RESULTS,
    ) -> str:
        """
        Get events within a specified time range.
        
        Args:
            start_time: The start time of the range in ISO 8601 format (YYYY-MM-DDTHH:MM).
            end_time: The end time of the range in ISO 8601 format (YYYY-MM-DDTHH:MM).
            max_results: Maximum number of events to return.
            
        Returns:
            A formatted list of events.
        """
        try:
            client = CalendarClient()
            
            # Ensure times have timezone information
            tz = pytz.timezone(config.TIMEZONE)
            
            if not start_time.endswith('Z') and '+' not in start_time:
                dt = datetime.strptime(start_time, config.DATE_FORMAT)
                start_time = tz.localize(dt).isoformat()
            
            if not end_time.endswith('Z') and '+' not in end_time:
                dt = datetime.strptime(end_time, config.DATE_FORMAT)
                end_time = tz.localize(dt).isoformat()
            
            events_result = client.service.events().list(
                calendarId=config.CALENDAR_ID,
                timeMin=start_time,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return f"No events found between {start_time} and {end_time}."
            
            formatted_events = client.format_events(events)
            return "Events found:\n\n" + "\n\n".join(formatted_events)
        except Exception as e:
            return f"Error getting events: {str(e)}"

@register_tool
class GetEventsByQueryTool(BaseTool):
    """Tool for searching events by query."""
    
    name = "get_calendar_events_by_query"
    description = "Search for events in the user's Google Calendar by keyword"
    
    def execute(
        self,
        query: str,
        max_results: int = config.MAX_CALENDAR_RESULTS,
    ) -> str:
        """
        Search for events by keyword.
        
        Args:
            query: The search term to find in event summaries and descriptions.
            max_results: Maximum number of events to return.
            
        Returns:
            A formatted list of events matching the query.
        """
        try:
            client = CalendarClient()
            
            # Set time range to include past and future events
            now = datetime.now().isoformat() + 'Z'
            one_year_future = (datetime.now() + timedelta(days=365)).isoformat() + 'Z'
            
            events_result = client.service.events().list(
                calendarId=config.CALENDAR_ID,
                q=query,
                timeMin=now,
                timeMax=one_year_future,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return f"No events found matching '{query}'."
            
            formatted_events = client.format_events(events)
            return f"Events matching '{query}':\n\n" + "\n\n".join(formatted_events)
        except Exception as e:
            return f"Error searching for events: {str(e)}"

@register_tool
class DeleteEventTool(BaseTool):
    """Tool for deleting a calendar event."""
    
    name = "delete_calendar_event"
    description = "Delete an event from the user's Google Calendar by event ID"
    
    def execute(self, event_id: str) -> str:
        """
        Delete a calendar event.
        
        Args:
            event_id: The ID of the event to delete.
            
        Returns:
            A confirmation message.
        """
        try:
            client = CalendarClient()
            
            # First get the event to confirm its details
            event = client.service.events().get(
                calendarId=config.CALENDAR_ID, 
                eventId=event_id
            ).execute()
            
            summary = event.get('summary', 'Unknown event')
            
            # Delete the event
            client.service.events().delete(
                calendarId=config.CALENDAR_ID, 
                eventId=event_id
            ).execute()
            
            return f"Event '{summary}' (ID: {event_id}) has been deleted."
        except Exception as e:
            return f"Error deleting event: {str(e)}"

@register_tool
class ModifyEventTool(BaseTool):
    """Tool for modifying a calendar event."""
    
    name = "modify_calendar_event"
    description = "Modify an existing event in the user's Google Calendar"
    
    def execute(
        self,
        event_id: str,
        summary: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> str:
        """
        Modify a calendar event.
        
        Args:
            event_id: The ID of the event to modify.
            summary: New title for the event (optional).
            location: New location for the event (optional).
            description: New description for the event (optional).
            start_time: New start time in ISO 8601 format (optional).
            end_time: New end time in ISO 8601 format (optional).
            
        Returns:
            A confirmation message with the updated event details.
        """
        try:
            client = CalendarClient()
            
            # Get the existing event
            event = client.service.events().get(
                calendarId=config.CALENDAR_ID, 
                eventId=event_id
            ).execute()
            
            # Update the fields that were provided
            if summary is not None:
                event['summary'] = summary
            if location is not None:
                event['location'] = location
            if description is not None:
                event['description'] = description
                
            # Update times if provided
            tz = pytz.timezone(config.TIMEZONE)
            
            if start_time is not None:
                if not start_time.endswith('Z') and '+' not in start_time:
                    dt = datetime.strptime(start_time, config.DATE_FORMAT)
                    start_time = tz.localize(dt).isoformat()
                event['start']['dateTime'] = start_time
                
            if end_time is not None:
                if not end_time.endswith('Z') and '+' not in end_time:
                    dt = datetime.strptime(end_time, config.DATE_FORMAT)
                    end_time = tz.localize(dt).isoformat()
                event['end']['dateTime'] = end_time
            
            # Update the event
            updated_event = client.service.events().update(
                calendarId=config.CALENDAR_ID, 
                eventId=event_id, 
                body=event
            ).execute()
            
            return (
                f"Event updated successfully!\n"
                f"Updated details:\n"
                f"{client.format_event(updated_event)}"
            )
        except Exception as e:
            return f"Error modifying event: {str(e)}"

@register_tool
class GetTodaysEventsTool(BaseTool):
    """Tool for getting today's events."""
    
    name = "get_todays_calendar_events"
    description = "Get all events scheduled for today from the user's Google Calendar"
    
    def execute(self) -> str:
        """
        Get all events scheduled for today.
        
        Returns:
            A formatted list of today's events.
        """
        try:
            client = CalendarClient()
            
            # Get today's date range
            tz = pytz.timezone(config.TIMEZONE)
            now = datetime.now(tz)
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=tz).isoformat()
            end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=tz).isoformat()
            
            events_result = client.service.events().list(
                calendarId=config.CALENDAR_ID,
                timeMin=start_of_day,
                timeMax=end_of_day,
                maxResults=config.MAX_CALENDAR_RESULTS,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return "No events scheduled for today."
            
            formatted_events = client.format_events(events)
            return "Today's events:\n\n" + "\n\n".join(formatted_events)
        except Exception as e:
            return f"Error getting today's events: {str(e)}" 