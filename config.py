import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://hackathonopenainous.openai.azure.com')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'o4-mini')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-small')
    AZURE_OPENAI_EMBEDDING_API_VERSION = os.getenv('AZURE_OPENAI_EMBEDDING_API_VERSION', '2023-05-15')
    
    # Regular OpenAI Configuration (fallback)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    @staticmethod
    def get_ai_provider():
        """Determine which AI provider to use"""
        if Config.AZURE_OPENAI_API_KEY:
            return 'azure'
        elif Config.OPENAI_API_KEY:
            return 'openai'
        elif Config.GEMINI_API_KEY:
            return 'gemini'
        else:
            return 'pattern_only'
    
    @staticmethod
    def validate():
        """Validate configuration - now allows pattern-only mode"""
        provider = Config.get_ai_provider()
        
        if provider == 'azure':
            if not Config.AZURE_OPENAI_ENDPOINT:
                raise ValueError("AZURE_OPENAI_ENDPOINT is required when using Azure OpenAI.")
        elif provider == 'gemini':
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required when using Gemini AI.")
        elif provider == 'pattern_only':
            print("⚠️  No AI API keys found. Running in pattern-only analysis mode.")
            print("🔍 Analysis will use regex patterns and heuristics only.")
            print("💡 For enhanced AI-powered analysis, provide an API key.")
            print("📌 Supported providers: Azure OpenAI, OpenAI, Gemini")
        
        return True
