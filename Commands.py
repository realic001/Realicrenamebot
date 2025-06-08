"""
Complete bot/commands.py file content for GitHub upload
Copy this entire content to your bot/commands.py file
"""

import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .database import Database
from .keyboards import BotKeyboards
from .utils import FileUtils, FormatUtils

logger = logging.getLogger(__name__)

class BotCommands:
    def __init__(self, database):
        """Initialize command handlers with database connection."""
        self.db = database
        self.keyboards = BotKeyboards()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        if not user or not update.message:
            return
        
        # Check if user is banned
        if self.db.is_banned(user.id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        # Add user to database
        self.db.add_user(user.id, user.username or "", user.first_name or "", user.last_name or "")
        
        welcome_text = f"""
🤖 **Welcome to Auto-Rename Bot, {user.first_name}!**

I'm your intelligent file renaming assistant with powerful features:

**🔄 Core Features:**
• Auto & Manual rename modes
• Custom format templates
• File support up to 5GB
• Thumbnail management

**🎨 Advanced Options:**
• Metadata editing
• Word replacement
• Statistics tracking
• Admin broadcasting

Send me a file to get started, or use the menu below!
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.main_menu()
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not update.message:
            return
            
        help_text = """
🤖 **Auto-Rename Bot Help**

**Main Commands:**
• `/start` - Start the bot and see main menu
• `/help` - Show this help message
• `/settings` - Configure your preferences
• `/format` - Manage format templates
• `/stats` - View your statistics

**File Operations:**
• Send any file/video to rename it
• Send photo to set as thumbnail
• Choose between auto/manual modes

**Format Variables:**
• `{title}` - File title
• `{artist}` - Artist name
• `{author}` - Author name
• `{album}` - Album name
• `{year}` - Year
• `{genre}` - Genre
• `{audio}` - Audio info
• `{video}` - Video info
• `{resolution}` - Video resolution
• `{duration}` - File duration
• `{size}` - File size

**Admin Commands (Admin Only):**
• `/ban <user_id>` - Ban a user
• `/unban <user_id>` - Unban a user
• `/admin add <user_id>` - Make user admin
• `/admin remove <user_id>` - Remove admin
• `/broadcast <message>` - Send to all users
• `/dump add <channel_id>` - Add dump channel
• `/dump remove <channel_id>` - Remove dump channel

**File Size Limit:** 5GB
**Supported Types:** Documents, Videos, Audio files

Use the inline buttons for easy navigation!
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ User data not found. Please use /start first.")
            return
        
        settings_text = f"""
⚙️ **Your Bot Settings**

**Current Configuration:**
• **Rename Mode:** {user_data.get('rename_mode', 'auto').title()}
• **Media Type:** {user_data.get('media_type', 'document').title()}
• **Format Template:** `{user_data.get('custom_format', '{title}')}`
• **Auto Thumbnail:** {'✅ Enabled' if user_data.get('auto_thumbnail') else '❌ Disabled'}

**Rename Modes:**
• **Auto** - Uses format templates
• **Manual** - Enter filename manually

**Media Types:**
• **Document** - Send as document file
• **Video** - Send as video with thumbnail

Use the buttons below to modify your settings:
        """
        
        await update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.settings_menu()
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        stats = self.db.get_user_stats(user_id)
        if not stats:
            await update.message.reply_text("❌ No statistics available. Process some files first!")
            return
        
        # Get user achievements
        achievements = self._get_user_achievements(stats)
        
        stats_text = f"""
📊 **Your Statistics**

**File Processing:**
• Files Renamed: {stats.get('files_renamed', 0)}
• Total Data Processed: {FileUtils.format_file_size(stats.get('total_size', 0))}
• Files This Week: {stats.get('recent_files', 0)}

**Account Info:**
• Member Since: {stats.get('join_date', 'Unknown')}
• Last Activity: {stats.get('last_activity', 'Unknown')}

**Achievements:**
{achievements}

Keep using the bot to unlock more achievements! 🏆
        """
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )

    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command"""
        if not update.message:
            return
            
        leaderboard = self.db.get_leaderboard(10)
        
        if not leaderboard:
            await update.message.reply_text("📊 No leaderboard data available yet.")
            return
        
        leaderboard_text = FormatUtils.format_leaderboard(leaderboard)
        leaderboard_text += "\n\nKeep processing files to climb the rankings! 🚀"
        
        await update.message.reply_text(
            leaderboard_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )

    def _get_user_achievements(self, user_stats):
        """Generate user achievements text"""
        achievements = []
        files_count = user_stats.get('files_renamed', 0)
        total_size = user_stats.get('total_size', 0)
        
        # File count achievements
        if files_count >= 1000:
            achievements.append("🏆 Master Renamer (1000+ files)")
        elif files_count >= 500:
            achievements.append("🥇 Expert User (500+ files)")
        elif files_count >= 100:
            achievements.append("🥈 Power User (100+ files)")
        elif files_count >= 10:
            achievements.append("🥉 Active User (10+ files)")
        elif files_count >= 1:
            achievements.append("🎯 First Steps (1+ files)")
        
        # Data size achievements
        if total_size >= 100 * 1024 * 1024 * 1024:  # 100GB
            achievements.append("💾 Data Master (100GB+ processed)")
        elif total_size >= 10 * 1024 * 1024 * 1024:  # 10GB
            achievements.append("📀 Heavy User (10GB+ processed)")
        elif total_size >= 1024 * 1024 * 1024:  # 1GB
            achievements.append("💿 Regular User (1GB+ processed)")
        
        # Special achievements
        recent_files = user_stats.get('recent_files', 0)
        if recent_files >= 50:
            achievements.append("⚡ Weekly Champion (50+ files this week)")
        elif recent_files >= 10:
            achievements.append("🔥 Active This Week (10+ files)")
        
        if not achievements:
            achievements.append("🌟 Getting Started")
        
        return "\n".join(f"• {achievement}" for achievement in achievements)
