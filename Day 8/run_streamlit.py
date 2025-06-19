#!/usr/bin/env python3
"""
Launcher script for Streamlit Agent App
This script helps you run the Streamlit app with proper setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import langchain
        import langchain_tavily
        import langgraph
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("Please create a .env file with your API keys:")
        print("Copy env_example.txt to .env and fill in your keys")
        return False

def run_streamlit_app(app_file="app.py"):
    """Run the Streamlit app"""
    if not check_dependencies():
        return False
    
    if not check_env_file():
        print("You can still try to run the app, but it may fail without API keys")
    
    print(f"🚀 Starting Streamlit app: {app_file}")
    print("The app will open in your browser automatically")
    print("Press Ctrl+C to stop the app")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_file])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🤖 AI Agent with Search - Streamlit Launcher")
    print("=" * 50)
    
    # Check which app to run
    if len(sys.argv) > 1:
        app_file = sys.argv[1]
    else:
        print("Choose which app to run:")
        print("1. Simple app (app.py)")
        print("2. Advanced app (streamlit_app.py)")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            app_file = "streamlit_app.py"
        else:
            app_file = "app.py"
    
    # Check if app file exists
    if not Path(app_file).exists():
        print(f"❌ App file {app_file} not found")
        return
    
    # Run the app
    run_streamlit_app(app_file)

if __name__ == "__main__":
    main() 