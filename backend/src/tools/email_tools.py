"""
Email-related tools for interacting with Gmail.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import sys
import os

# Add parent directory to path if running as a script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.base import BaseTool, register_tool
from src.google_authenticator import GoogleAuthenticator
import src.config as config

class EmailClient:
    """Handles interaction with the Gmail API."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the email client."""
        self.authenticator = GoogleAuthenticator()
        self.service = build('gmail', 'v1', credentials=self.authenticator.creds)
    
    def format_email(self, email_data: Dict[str, Any]) -> str:
        """Format an email dictionary into a readable string with type indicator."""
        sender = email_data.get('sender', 'Unknown sender')
        subject = email_data.get('subject', 'No subject')
        content = email_data.get('content', 'No content')
        date = email_data.get('date', 'Unknown date')
        email_id = email_data.get('id', 'No ID')
        
        return (
            f"[EMAIL]\n"
            f"📧 {sender}\n"
            f"📅 {date}\n"
            f"📌 {subject}\n"
            f"{content}\n"
        )
    
    def extract_email_content(self, message: Dict[str, Any]) -> str:
        """
        Extract the content of an email, prioritizing plain text over HTML.
        """
        try:
            # Check if the email has parts
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':  # Prioritize plain text
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/html':  # Fallback to HTML
                        if 'data' in part['body']:
                            html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            return self._sanitize_html(html_content)
            else:
                # Handle case where email has no parts (e.g., single part emails)
                if message['payload']['mimeType'] == 'text/plain':
                    if 'data' in message['payload']['body']:
                        return base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                elif message['payload']['mimeType'] == 'text/html':
                    if 'data' in message['payload']['body']:
                        html_content = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                        return self._sanitize_html(html_content)
        except Exception as e:
            return f"Unable to decode email content: {e}"
        
        return "No readable content found in the email."
    
    def _sanitize_html(self, html_content: str) -> str:
        """Convert HTML content to plain text and remove unwanted formatting."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            return f"Unable to parse HTML content: {e}"
    
    def get_email_date(self, message: Dict[str, Any]) -> str:
        """Extract the date from email headers."""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'date':
                return header['value']
        return "Unknown date"

@register_tool
class FetchLatestEmailsTool(BaseTool):
    """Tool for fetching the latest emails."""
    
    name = "fetch_latest_emails"
    description = "Get the most recent emails from the user's Gmail inbox"
    
    def execute(self, max_results: int = config.MAX_EMAIL_RESULTS) -> str:
        """
        Fetch the latest emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to return.
            
        Returns:
            A formatted list of email details.
        """
        try:
            client = EmailClient()
            
            # Fetch the latest emails
            results = client.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "No emails found in your inbox."
            
            email_details = []
            
            for message_info in messages:
                try:
                    email_id = message_info['id']
                    message = client.service.users().messages().get(
                        userId='me', 
                        id=email_id, 
                        format='full'
                    ).execute()
                    
                    # Extract email data
                    email_data = {
                        'id': email_id,
                        'sender': None,
                        'subject': None,
                        'content': None,
                        'date': client.get_email_date(message)
                    }
                    
                    # Extract headers
                    headers = message['payload']['headers']
                    for header in headers:
                        if header['name'] == 'From':
                            email_data['sender'] = header['value']
                        elif header['name'] == 'Subject':
                            email_data['subject'] = header['value']
                    
                    # Extract content
                    email_data['content'] = client.extract_email_content(message)
                    
                    # Format and add to results
                    email_details.append(client.format_email(email_data))
                except Exception as e:
                    continue  # Skip this email if there's an error
            
            if not email_details:
                return "Could not process any emails."
            
            return "\n".join(email_details)
        except Exception as e:
            return f"Error fetching emails: {str(e)}"

@register_tool
class SearchEmailsTool(BaseTool):
    """Tool for searching emails by query."""
    
    name = "search_emails"
    description = "Search for emails in Gmail by keyword or query"
    
    def execute(
        self,
        query: str,
        max_results: int = config.MAX_EMAIL_RESULTS,
    ) -> str:
        """
        Search for emails by keyword or query.
        
        Args:
            query: Search term to find in emails.
            max_results: Maximum number of emails to return.
            
        Returns:
            A formatted list of email details matching the query.
        """
        try:
            client = EmailClient()
            
            # Search for emails
            results = client.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return f"No emails found matching '{query}'."
            
            email_details = []
            
            for message_info in messages:
                try:
                    email_id = message_info['id']
                    message = client.service.users().messages().get(
                        userId='me', 
                        id=email_id, 
                        format='full'
                    ).execute()
                    
                    # Extract email data
                    email_data = {
                        'id': email_id,
                        'sender': None,
                        'subject': None,
                        'content': None,
                        'date': client.get_email_date(message)
                    }
                    
                    # Extract headers
                    headers = message['payload']['headers']
                    for header in headers:
                        if header['name'] == 'From':
                            email_data['sender'] = header['value']
                        elif header['name'] == 'Subject':
                            email_data['subject'] = header['value']
                    
                    # Extract content
                    email_data['content'] = client.extract_email_content(message)
                    
                    # Format and add to results
                    email_details.append(client.format_email(email_data))
                except Exception as e:
                    continue  # Skip this email if there's an error
            
            if not email_details:
                return f"Could not process any emails matching '{query}'."
            
            return "\n".join(email_details)
        except Exception as e:
            return f"Error searching emails: {str(e)}"

@register_tool
class FetchEmailsByDateTool(BaseTool):
    """Tool for fetching emails by date range."""
    
    name = "fetch_emails_by_date"
    description = "Get emails from Gmail within a specific date range"
    
    def execute(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        max_results: int = config.MAX_EMAIL_RESULTS,
    ) -> str:
        """
        Fetch emails within a specific date range.
        
        Args:
            start_date: Start date in 'YYYY/MM/DD' format.
            end_date: End date in 'YYYY/MM/DD' format (defaults to today if not provided).
            max_results: Maximum number of emails to return.
            
        Returns:
            A formatted list of email details within the date range.
        """
        try:
            client = EmailClient()
            
            # Construct the date query
            query = f"after:{start_date}"
            if end_date:
                query += f" before:{end_date}"
            
            # Search for emails
            results = client.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                date_range = f"from {start_date}" + (f" to {end_date}" if end_date else "")
                return f"No emails found {date_range}."
            
            email_details = []
            
            for message_info in messages:
                try:
                    email_id = message_info['id']
                    message = client.service.users().messages().get(
                        userId='me', 
                        id=email_id, 
                        format='full'
                    ).execute()
                    
                    # Extract email data
                    email_data = {
                        'id': email_id,
                        'sender': None,
                        'subject': None,
                        'content': None,
                        'date': client.get_email_date(message)
                    }
                    
                    # Extract headers
                    headers = message['payload']['headers']
                    for header in headers:
                        if header['name'] == 'From':
                            email_data['sender'] = header['value']
                        elif header['name'] == 'Subject':
                            email_data['subject'] = header['value']
                    
                    # Extract content
                    email_data['content'] = client.extract_email_content(message)
                    
                    # Format and add to results
                    email_details.append(client.format_email(email_data))
                except Exception as e:
                    continue  # Skip this email if there's an error
            
            if not email_details:
                date_range = f"from {start_date}" + (f" to {end_date}" if end_date else "")
                return f"No emails found {date_range}."
            
            return "\n".join(email_details)
        except Exception as e:
            return f"Error fetching emails by date: {str(e)}"

@register_tool
class SendEmailTool(BaseTool):
    """Tool for sending emails via Gmail."""
    
    name = "send_email"
    description = "Send an email using Gmail"
    
    def execute(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> str:
        """
        Send an email using Gmail.
        
        Args:
            to: Recipient email address.
            subject: Email subject.
            body: Email body content.
            cc: Optional CC recipient email address.
            bcc: Optional BCC recipient email address.
            
        Returns:
            A confirmation message indicating whether the email was sent successfully.
        """
        try:
            client = EmailClient()
            
            # Create the email message
            message = {
                'raw': self._create_message(to, subject, body, cc, bcc)
            }
            
            # Send the email
            sent_message = client.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return f"Email sent successfully! Message ID: {sent_message['id']}"
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    def _create_message(self, to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None) -> str:
        """Create a properly formatted email message."""
        # Create the email headers
        headers = [
            f"To: {to}",
            f"Subject: {subject}"
        ]
        
        if cc:
            headers.append(f"Cc: {cc}")
        if bcc:
            headers.append(f"Bcc: {bcc}")
        
        # Combine headers and body
        message = "\r\n".join(headers) + "\r\n\r\n" + body
        
        # Encode the message in base64url format
        return base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8') 