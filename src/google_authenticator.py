"""
Google API authentication handler.
"""
import os
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleAuthenticator:
    """Handles authentication with Google APIs."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GoogleAuthenticator, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the authenticator with the required scopes."""
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.creds = None
        self.token_path = 'keys/token.json'
        self.credentials_path = 'keys/credentials.json'
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google APIs."""
        try:
            # Ensure the keys directory exists
            os.makedirs('keys', exist_ok=True)
            
            # Check if token file exists
            if os.path.exists(self.token_path):
                try:
                    # Load credentials from the token file
                    self.creds = Credentials.from_authorized_user_info(
                        info=eval(open(self.token_path, "r").read()), 
                        scopes=self.scopes
                    )
                except Exception as e:
                    print(f"Error loading token: {e}")
                    self.creds = None
            
            # If credentials don't exist or are invalid, go through authentication flow
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        # Refresh token if expired
                        self.creds.refresh(Request())
                    except Exception as e:
                        print(f"Error refreshing token: {e}")
                        self.creds = None
                
                # If still no valid credentials, start the OAuth flow
                if not self.creds:
                    if not os.path.exists(self.credentials_path):
                        sys.stderr.write(
                            "Error: No credentials found. Please place your "
                            "credentials.json file in the keys directory.\n"
                        )
                        sys.stderr.write(
                            "Visit https://console.developers.google.com/ "
                            "to create credentials for Calendar and Gmail APIs.\n"
                        )
                        raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
                    
                    # Start the OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    self.creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for future use
                    with open(self.token_path, 'w') as token:
                        token.write(str(self.creds.to_json()))
        
        except Exception as e:
            sys.stderr.write(f"Authentication error: {e}\n")
            sys.stderr.write("Some functionality requiring Google API access will be limited.\n")
            self.creds = None 