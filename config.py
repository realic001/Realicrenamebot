"""
Configuration module for the Telegram Auto-Rename Bot.
Handles environment variables and default settings.
"""

import os
from typing import List, Optional

class Config:
    """Configuration class for bot settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Required settings
        self.BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
        if not self.BOT_TOKEN:
            print("⚠️  BOT_TOKEN environment variable not set. Please set it to run the bot.")
            self.BOT_TOKEN = "placeholder_token"
        
        # Owner and admin settings
        self.OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
        if not self.OWNER_ID:
            print("⚠️  OWNER_ID environment variable not set. Please set it to enable admin features.")
            self.OWNER_ID = 0
        
        # Optional webhook settings
        self.USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "false").lower() == "true"
        self.WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
        self.PORT: int = int(os.getenv("PORT", "5000"))
        
        # File processing settings
        self.MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(5 * 1024 * 1024 * 1024)))  # 5GB
        self.DOWNLOAD_PATH: str = os.getenv("DOWNLOAD_PATH", "./downloads")
        self.TEMP_PATH: str = os.getenv("TEMP_PATH", "./temp")
        
        # Default format templates
        self.DEFAULT_FORMAT: str = os.getenv("DEFAULT_FORMAT", "{title}")
        
        # Create necessary directories
        os.makedirs(self.DOWNLOAD_PATH, exist_ok=True)
        os.makedirs(self.TEMP_PATH, exist_ok=True)
        
        # Database settings
        self.DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bot_data.db")
        
        # Logging settings
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        
        # Rate limiting
        self.RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
    def is_owner(self, user_id: int) -> bool:
        """Check if user is the bot owner."""
        return user_id == self.OWNER_ID
    
    def get_help_text(self) -> str:
        """Get help text for the bot."""
        return """
🤖 **Auto-Rename Bot Help**

**Main Features:**
• `/start` - Start the bot and see main menu
• `/settings` - Access bot settings
• `/format` - Set custom rename format
• `/stats` - View your statistics

**File Operations:**
• Send any file/video to rename it
• Send photo to set as thumbnail
• Auto/Manual rename modes available

**Admin Commands:**
• `/ban <user_id>` - Ban a user
• `/unban <user_id>` - Unban a user  
• `/admin <user_id>` - Make user admin
• `/broadcast <message>` - Broadcast to all users
• `/dump <channel_id>` - Add dump channel

**Format Variables:**
• `{title}` - File title
• `{author}` - Author name
• `{artist}` - Artist name
• `{audio}` - Audio track info
• `{video}` - Video info

**File Size Limit:** 5GB
**Supported Types:** Documents, Videos, Audio

Use inline buttons for easy navigation!
        """
