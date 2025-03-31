#!/usr/bin/env python3
"""
Main entry point for the personal assistant application.
"""

import os
import sys
import argparse
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Add parent directory to path if running as a script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from src
from src.agent_manager import MultiAgentSystem, AgentManager
import src.config as config

# Initialize colorama
init()

def print_banner():
    """Print a welcome banner."""
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}           Personal Assistant with Multiple Agents{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def print_stream(stream_generator):
    """Print the streaming response."""
    print(f"{Fore.GREEN}Assistant:{Style.RESET_ALL} ", end="", flush=True)
    try:
        for chunk in stream_generator:
            if isinstance(chunk, dict):
                # Handle dictionary chunks (when using AgentManager directly)
                if chunk["type"] == "content":
                    print(chunk["content"], end="", flush=True)
                elif chunk["type"] == "tool_start":
                    print(f"\n[{Fore.YELLOW}TOOL{Style.RESET_ALL}] Running {chunk['name']}...\n", end="", flush=True)
                elif chunk["type"] == "tool_result":
                    result = chunk["result"].replace("\n", "\n  ")  # Indent result
                    print(f"  {result}\n", end="", flush=True)
                elif chunk["type"] == "tool_error":
                    print(f"\n[{Fore.RED}ERROR{Style.RESET_ALL}] {chunk['error']}\n", end="", flush=True)
                elif chunk["type"] == "second_response_start":
                    print(f"\n[{Fore.GREEN}ASSISTANT{Style.RESET_ALL}] ", end="", flush=True)
            else:
                # Handle string chunks (when using MultiAgentSystem)
                print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\n{Fore.RED}Error during streaming: {e}{Style.RESET_ALL}")
    print()  # Add a newline at the end

def main():
    """Run the personal assistant application."""
    # Load environment variables
    load_dotenv()
    
    # Make sure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Personal Assistant")
    parser.add_argument("--multi", action="store_true", help="Use multi-agent system")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Set debug mode if requested
    if args.debug:
        os.environ["DEBUG_MODE"] = "True"
    
    # Check if API key is available
    if not config.OPENAI_API_KEY:
        print(f"{Fore.RED}Error: OPENAI_API_KEY environment variable not set.{Style.RESET_ALL}")
        sys.exit(1)
    
    # Print welcome banner
    print_banner()
    print(f"Welcome to your Personal Assistant! Type {Fore.YELLOW}exit{Style.RESET_ALL} to end the conversation.")
    
    # Initialize the assistant
    if args.multi:
        print(f"Using {Fore.CYAN}multi-agent{Style.RESET_ALL} system with specialized agents")
        assistant = MultiAgentSystem()
    else:
        print(f"Using {Fore.CYAN}single-agent{Style.RESET_ALL} system")
        assistant = AgentManager()
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input(f"\n{Fore.CYAN}You:{Style.RESET_ALL} ")
        
        # Check for exit conditions
        if user_input.strip().lower() in ['exit', 'quit', 'stop', 'bye']:
            print(f"\n{Fore.GREEN}Assistant:{Style.RESET_ALL} Goodbye! Have a great day.")
            break
        
        # Process the user input
        try:
            stream_generator = assistant.stream_chat(user_input)
            print_stream(stream_generator)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()