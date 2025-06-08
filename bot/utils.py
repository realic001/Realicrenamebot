"""
Complete bot/utils.py file content for GitHub upload
Copy this entire content to your bot/utils.py file
"""

import os
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        if not filename:
            return ""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_video_file(filename: str) -> bool:
        """Check if file is a video file."""
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        return FileUtils.get_file_extension(filename) in video_extensions
    
    @staticmethod
    def is_audio_file(filename: str) -> bool:
        """Check if file is an audio file."""
        audio_extensions = {'.mp3', '.flac', '.aac', '.ogg', '.wav', '.m4a', '.wma'}
        return FileUtils.get_file_extension(filename) in audio_extensions
    
    @staticmethod
    def is_document_file(filename: str) -> bool:
        """Check if file is a document file."""
        doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
        return FileUtils.get_file_extension(filename) in doc_extensions
    
    @staticmethod
    def is_archive_file(filename: str) -> bool:
        """Check if file is an archive file."""
        archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
        return FileUtils.get_file_extension(filename) in archive_extensions
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Get general file type category."""
        if FileUtils.is_video_file(filename):
            return "video"
        elif FileUtils.is_audio_file(filename):
            return "audio"
        elif FileUtils.is_document_file(filename):
            return "document"
        elif FileUtils.is_archive_file(filename):
            return "archive"
        else:
            return "unknown"
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """Ensure directory exists, create if it doesn't."""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False


class TextUtils:
    """Utility functions for text processing."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing/replacing invalid characters."""
        if not filename:
            return "unnamed_file"
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove multiple consecutive spaces and underscores
        filename = re.sub(r'[ _]+', '_', filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure filename isn't empty
        if not filename:
            filename = "unnamed_file"
        
        # Limit length (keep extension)
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        
        return name + ext
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length with ellipsis."""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def extract_words(text: str) -> List[str]:
        """Extract words from text."""
        if not text:
            return []
        
        # Extract alphanumeric words
        words = re.findall(r'\b\w+\b', text.lower())
        return list(set(words))  # Remove duplicates
    
    @staticmethod
    def replace_words(text: str, replacements: Dict[str, str]) -> str:
        """Replace words in text based on replacement dictionary."""
        if not text or not replacements:
            return text
        
        result = text
        for old_word, new_word in replacements.items():
            # Case-insensitive word replacement
            pattern = r'\b' + re.escape(old_word) + r'\b'
            result = re.sub(pattern, new_word, result, flags=re.IGNORECASE)
        
        return result
    
    @staticmethod
    def format_template(template: str, variables: Dict[str, str]) -> str:
        """Format template string with variables."""
        if not template:
            return ""
        
        result = template
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            result = result.replace(placeholder, str(var_value))
        
        return result
    
    @staticmethod
    def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
        """Extract potential metadata from filename patterns."""
        metadata = {}
        
        if not filename:
            return metadata
        
        # Remove extension for analysis
        name_without_ext = os.path.splitext(filename)[0]
        
        # Common patterns
        patterns = {
            'year': r'\b(19|20)\d{2}\b',
            'season_episode': r'[Ss](\d+)[Ee](\d+)',
            'resolution': r'\b(720p|1080p|1440p|2160p|4K)\b',
            'quality': r'\b(HD|FHD|UHD|BluRay|WEB|DVDRip)\b'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, name_without_ext, re.IGNORECASE)
            if match:
                metadata[key] = match.group()
        
        return metadata


class TimeUtils:
    """Utility functions for time and date operations."""
    
    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format timestamp to readable string."""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Unknown"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to readable string."""
        if seconds <= 0:
            return "0:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def time_ago(timestamp: float) -> str:
        """Get human readable time difference from timestamp."""
        try:
            now = datetime.now()
            dt = datetime.fromtimestamp(timestamp)
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
        except Exception:
            return "Unknown"
    
    @staticmethod
    def get_current_timestamp() -> float:
        """Get current timestamp."""
        return time.time()
    
    @staticmethod
    def is_recent(timestamp: float, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours."""
        try:
            now = time.time()
            return (now - timestamp) < (hours * 3600)
        except Exception:
            return False


class ValidationUtils:
    """Utility functions for validation."""
    
    @staticmethod
    def is_valid_user_id(user_id_str: str) -> bool:
        """Validate if string is a valid Telegram user ID."""
        try:
            user_id = int(user_id_str)
            return 1 <= user_id <= 999999999999
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_channel_id(channel_id_str: str) -> bool:
        """Validate if string is a valid Telegram channel ID."""
        try:
            channel_id = int(channel_id_str)
            return channel_id < 0  # Channels have negative IDs
        except ValueError:
            return False
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, str]:
        """Validate filename and return result with message."""
        if not filename:
            return False, "Filename cannot be empty"
        
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                return False, f"Invalid character '{char}' in filename"
        
        if filename.startswith('.'):
            return False, "Filename cannot start with a dot"
        
        return True, "Valid filename"
    
    @staticmethod
    def validate_format_template(template: str) -> tuple[bool, str]:
        """Validate format template string."""
        if not template:
            return False, "Template cannot be empty"
        
        # Check for valid template variables
        valid_vars = {
            'title', 'artist', 'author', 'album', 'genre', 'year',
            'audio', 'video', 'codec', 'resolution', 'duration', 'size'
        }
        
        # Extract variables from template
        import re
        variables = re.findall(r'\{(\w+)\}', template)
        
        invalid_vars = [var for var in variables if var not in valid_vars]
        if invalid_vars:
            return False, f"Invalid variables: {', '.join(invalid_vars)}"
        
        return True, "Valid template"


class FormatUtils:
    """Utility functions for formatting data."""
    
    @staticmethod
    def format_user_stats(stats: Dict[str, Any]) -> str:
        """Format user statistics for display."""
        if not stats:
            return "No statistics available"
        
        lines = [
            f"Files Processed: {stats.get('files_renamed', 0)}",
            f"Total Size: {FileUtils.format_file_size(stats.get('total_size', 0))}",
            f"Member Since: {stats.get('join_date', 'Unknown')}",
            f"Last Activity: {stats.get('last_activity', 'Unknown')}"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_file_info(file_info: Dict[str, Any]) -> str:
        """Format file information for display."""
        if not file_info:
            return "No file information available"
        
        lines = [
            f"📁 **File Information**",
            f"",
            f"**Name:** {file_info.get('filename', 'Unknown')}",
            f"**Size:** {FileUtils.format_file_size(file_info.get('size', 0))}",
            f"**Type:** {file_info.get('type', 'Unknown').title()}"
        ]
        
        # Add type-specific info
        if file_info.get('duration'):
            lines.append(f"**Duration:** {TimeUtils.format_duration(file_info['duration'])}")
        
        if file_info.get('resolution'):
            lines.append(f"**Resolution:** {file_info['resolution']}")
        
        if file_info.get('codec'):
            lines.append(f"**Codec:** {file_info['codec'].upper()}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_leaderboard(users: List[Dict[str, Any]]) -> str:
        """Format leaderboard for display."""
        if not users:
            return "No users in leaderboard"
        
        lines = ["🏆 **Top Users**", ""]
        
        for i, user in enumerate(users, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            username = user.get('username') or user.get('first_name', 'Anonymous')
            files = user.get('files_renamed', 0)
            size = FileUtils.format_file_size(user.get('total_size', 0))
            
            lines.append(f"{emoji} **{username}**")
            lines.append(f"   📁 {files} files • 💾 {size}")
            lines.append("")
        
        return "\n".join(lines)


class SecurityUtils:
    """Utility functions for security and validation."""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent injection."""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        
        result = text
        for char in dangerous_chars:
            result = result.replace(char, '')
        
        return result.strip()
    
    @staticmethod
    def is_safe_path(path: str) -> bool:
        """Check if file path is safe (no directory traversal)."""
        if not path:
            return False
        
        # Normalize path
        normalized = os.path.normpath(path)
        
        # Check for directory traversal attempts
        if '..' in normalized or normalized.startswith('/'):
            return False
        
        return True
    
    @staticmethod
    def validate_file_size(size: int, max_size: int) -> tuple[bool, str]:
        """Validate file size against maximum allowed."""
        if size <= 0:
            return False, "Invalid file size"
        
        if size > max_size:
            return False, f"File too large. Max: {FileUtils.format_file_size(max_size)}"
        
        return True, "Valid file size"
