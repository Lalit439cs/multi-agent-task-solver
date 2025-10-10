import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the multi-agent system."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Google Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Search Configuration
    SEARCH_ENABLED: bool = os.getenv("SEARCH_ENABLED", "true").lower() == "true"
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "3"))
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "60"))  # seconds
    
    # File I/O Configuration
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY and not cls.GOOGLE_API_KEY:
            raise ValueError("At least one of OPENAI_API_KEY or GOOGLE_API_KEY must be set")
        return True

# Create temp directory if it doesn't exist
os.makedirs(Config.TEMP_DIR, exist_ok=True)
