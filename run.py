#!/usr/bin/env python3
"""
Secure Prompt Shield - Local Runner
This script loads environment variables and starts the Flask application.
"""

import os
import sys
from dotenv import load_dotenv
from config import Config

def main():
    """Main function to run the application"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated successfully!")
        print(f"🤖 Using Azure OpenAI deployment: {Config.AZURE_OPENAI_DEPLOYMENT}")
        print(f"🔗 Azure OpenAI endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📝 Please check your .env file and ensure all Azure OpenAI settings are correct.")
        sys.exit(1)
    
    # Import and run the Flask app
    try:
        from app import app
        print("🚀 Starting Secure Prompt Shield...")
        print("🌐 Access the application at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=Config.DEBUG
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📦 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Application Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
