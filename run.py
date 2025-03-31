#!/usr/bin/env python3
"""
Wrapper script to check for necessary files and run the personal assistant.
"""
import os
import sys
import argparse
from colorama import Fore, Style, init

# Initialize colorama
init()

def check_prerequisites():
    """Check if all prerequisites are met to run the assistant."""
    # Check if src directory exists
    if not os.path.isdir("src"):
        print(f"{Fore.RED}Error: 'src' directory not found.{Style.RESET_ALL}")
        return False
    
    # Check if main.py exists
    if not os.path.isfile("src/main.py"):
        print(f"{Fore.RED}Error: 'src/main.py' not found.{Style.RESET_ALL}")
        return False
        
    # Check for Python packages
    try:
        import openai
        import dotenv
        import pytz
        import bs4
        import pydantic
        from google.oauth2.credentials import Credentials
    except ImportError as e:
        print(f"{Fore.RED}Error: Missing required package: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please run: pip install -r requirements.txt{Style.RESET_ALL}")
        return False
    
    # Ensure keys directory exists
    os.makedirs("keys", exist_ok=True)
    
    # Check for credentials.json
    if not os.path.isfile("keys/credentials.json"):
        print(f"{Fore.YELLOW}Warning: 'keys/credentials.json' not found.{Style.RESET_ALL}")
        print(f"You need to place your Google API credentials file at keys/credentials.json")
        print(f"Visit https://console.developers.google.com/ to create credentials for Calendar and Gmail APIs.")
        print()
    
    # Check for .env file with OPENAI_API_KEY
    if not os.path.isfile(".env"):
        print(f"{Fore.YELLOW}Warning: '.env' file not found.{Style.RESET_ALL}")
        print(f"Creating a sample .env file...")
        with open(".env", "w") as f:
            f.write("""# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# System Configuration
DEBUG_MODE=False  # Set to True for verbose logging
TIMEZONE=America/New_York  # User's local timezone

# Google API Configuration
# Place your credentials.json file in the keys directory
CALENDAR_ID=primary  # Usually 'primary' for the main calendar

# UI Configuration
ENABLE_COLORS=True  # Enable colorful terminal output

# Data Storage
MEMORY_FILE=data/memory.json  # Path to store conversation history
""")
        print(f"Please edit the .env file and add your OpenAI API key.")
        print()
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run the Personal Assistant")
    parser.add_argument("--multi", action="store_true", help="Use multi-agent system")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--check", action="store_true", help="Only check prerequisites without running")
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # If only checking, exit now
    if args.check:
        print(f"{Fore.GREEN}All checks passed. You can run the assistant.{Style.RESET_ALL}")
        sys.exit(0)
    
    # Build command
    cmd = [sys.executable, "src/main.py"]
    if args.multi:
        cmd.append("--multi")
    if args.debug:
        cmd.append("--debug")
    
    # Run the main program
    print(f"{Fore.GREEN}Starting personal assistant...{Style.RESET_ALL}")
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main() 