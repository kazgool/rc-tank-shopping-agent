"""
Configuration Management for RC Tank Shopping Agent

This module loads and manages all configuration settings from environment variables
and provides them to other parts of the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.absolute()

# Output directories
OUTPUT_DIR = ROOT_DIR / "output"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = OUTPUT_DIR / "logs"

# Data directory
DATA_DIR = ROOT_DIR / "data"

# Ensure all directories exist
for directory in [SCREENSHOTS_DIR, REPORTS_DIR, LOGS_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Config:
    """
    Configuration class that holds all application settings.
    Settings are loaded from environment variables with sensible defaults.
    """
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-4-vision-preview"  # Model for vision analysis
    OPENAI_TEXT_MODEL = "gpt-4-turbo-preview"  # Model for text generation
    
    # Browser Configuration
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    BROWSER_TYPE = "chromium"  # chromium, firefox, or webkit
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Platform Credentials (optional)
    AMAZON_EMAIL = os.getenv("AMAZON_EMAIL", "")
    AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD", "")
    EMAG_EMAIL = os.getenv("EMAG_EMAIL", "")
    EMAG_PASSWORD = os.getenv("EMAG_PASSWORD", "")
    TEMU_EMAIL = os.getenv("TEMU_EMAIL", "")
    TEMU_PASSWORD = os.getenv("TEMU_PASSWORD", "")
    
    # Rate Limiting (in seconds)
    MIN_DELAY = float(os.getenv("MIN_DELAY_BETWEEN_ACTIONS", "2"))
    MAX_DELAY = float(os.getenv("MAX_DELAY_BETWEEN_ACTIONS", "5"))
    
    # Search Configuration
    MAX_PRODUCTS_TO_ANALYZE = int(os.getenv("MAX_PRODUCTS_TO_ANALYZE", "5"))
    SEARCH_TIMEOUT = 30  # seconds
    PAGE_LOAD_TIMEOUT = 30  # seconds
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "shopping_agent.log"
    
    # Platform URLs
    PLATFORMS = {
        "amazon": {
            "name": "Amazon",
            "url": "https://www.amazon.com",
            "search_url": "https://www.amazon.com/s?k={query}",
            "enabled": True
        },
        "emag": {
            "name": "eMAG",
            "url": "https://www.emag.ro",
            "search_url": "https://www.emag.ro/search/{query}",
            "enabled": True
        },
        "temu": {
            "name": "Temu",
            "url": "https://www.temu.com",
            "search_url": "https://www.temu.com/search_result.html?search_key={query}",
            "enabled": True
        }
    }
    
    @classmethod
    def validate(cls):
        """
        Validate that all required configuration is present.
        Raises ValueError if critical configuration is missing.
        """
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set. Please add it to your .env file.")
        
        if cls.MIN_DELAY > cls.MAX_DELAY:
            errors.append("MIN_DELAY cannot be greater than MAX_DELAY")
        
        if errors:
            error_message = "Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors)
            raise ValueError(error_message)
    
    @classmethod
    def get_platform_config(cls, platform_name: str) -> dict:
        """
        Get configuration for a specific platform.
        
        Args:
            platform_name: Name of the platform (amazon, emag, temu)
            
        Returns:
            Dictionary with platform configuration
            
        Raises:
            KeyError: If platform is not supported
        """
        if platform_name not in cls.PLATFORMS:
            raise KeyError(f"Platform '{platform_name}' is not supported. "
                         f"Supported platforms: {', '.join(cls.PLATFORMS.keys())}")
        return cls.PLATFORMS[platform_name]


# Configure logging
logger.add(
    Config.LOG_FILE,
    rotation="10 MB",
    retention="10 days",
    level=Config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

logger.info("Configuration loaded successfully")
