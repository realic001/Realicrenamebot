"""
Complete bot/__init__.py file content for GitHub upload
Copy this entire content to your bot/__init__.py file
"""

"""
Bot package for Telegram Auto-Rename Bot

This package contains all the core functionality for the bot including:
- Database management
- File processing and renaming
- User interface and keyboards
- Admin controls and broadcasting
- Utility functions
"""

from .database import Database
from .handlers import BotHandlers
from .keyboards import BotKeyboards
from .admin import AdminHandlers
from .file_manager import FileManager
from .utils import FileUtils, TextUtils, TimeUtils, ValidationUtils, FormatUtils, SecurityUtils
from .commands import BotCommands

__version__ = "1.0.0"
__author__ = "Auto-Rename Bot Developer"
__description__ = "Telegram bot for automatic file renaming with advanced features"

__all__ = [
    'Database',
    'BotHandlers', 
    'BotKeyboards',
    'AdminHandlers',
    'FileManager',
    'FileUtils',
    'TextUtils', 
    'TimeUtils',
    'ValidationUtils',
    'FormatUtils',
    'SecurityUtils',
    'BotCommands'
]