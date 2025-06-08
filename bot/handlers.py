"""
Main bot handlers for user interactions and file processing.
"""

import os
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from telegram import Update, Message, Document, Video, PhotoSize
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError

from .database import Database
from .keyboards import BotKeyboards
from .utils import FileUtils, TextUtils, TimeUtils
from .file_manager import FileManager
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Main handlers for bot functionality."""
    
    def __init__(self, database: Database):
        """Initialize handlers with database connection."""
        self.db = database
        self.config = Config()
        self.keyboards = BotKeyboards()
        self.file_manager = FileManager(database)
        self.user_states = {}  # Store user conversation states
        self.processing_files = {}  # Track file processing status
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        if not user or not update.message:
            return
        
        # Check if user is banned
        if self.db.is_banned(user.id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        # Add user to database
        self.db.add_user(user.id, user.username or "", user.first_name or "", user.last_name or "")
        
        # Send welcome image first
        try:
            with open('bot_welcome.png', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"🤖 **Welcome to Auto-Rename Bot, {user.first_name}!**"
                )
        except FileNotFoundError:
            logger.warning("Welcome image not found, sending text-only welcome")
        
        welcome_text = f"""
⚔️ **hlw I am zoro AutoRename Bot, {user.first_name}!** 

🔥 Master of file renaming with legendary powers:

**⚔️ Zoro's Arsenal:**
• Auto & Manual rename mastery
• Custom format blade techniques  
• File support up to 5GB
• Thumbnail extraction skills

**🎯 Advanced Abilities:**
• Metadata editing prowess
• Word replacement techniques
• Battle statistics tracking
• Admin command powers

Send me a file to witness my renaming mastery! 👇
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.main_menu()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        await update.message.reply_text(
            self.config.get_help_text(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /settings command."""
        user_id = update.effective_user.id
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ User data not found. Please use /start first.")
            return
        
        settings_text = f"""
⚙️ **Your Current Settings**

**Rename Mode:** {user_data.get('rename_mode', 'auto').title()}
**Media Type:** {user_data.get('media_type', 'document').title()}
**Custom Format:** `{user_data.get('custom_format', '{title}')}`
**Auto Thumbnail:** {'✅ Enabled' if user_data.get('auto_thumbnail') else '❌ Disabled'}

Choose a setting to modify:
        """
        
        await update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.settings_menu()
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command."""
        user_id = update.effective_user.id
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        stats = self.db.get_user_stats(user_id)
        if not stats:
            await update.message.reply_text("❌ No statistics available.")
            return
        
        stats_text = f"""
📊 **Your Statistics**

**Files Renamed:** {stats.get('files_renamed', 0)}
**Total Size Processed:** {FileUtils.format_file_size(stats.get('total_size', 0))}
**Member Since:** {stats.get('join_date', 'Unknown')}
**Last Activity:** {stats.get('last_activity', 'Unknown')}
**Recent Files (7 days):** {stats.get('recent_files', 0)}

Keep using the bot to improve your stats! 📈
        """
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )
    
    async def format_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /format command."""
        user_id = update.effective_user.id
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        format_help = """
📝 **Format Template Guide**

**Available Variables:**
• `{title}` - File title/name
• `{author}` - Author name
• `{artist}` - Artist name
• `{album}` - Album name
• `{genre}` - Genre
• `{year}` - Year
• `{audio}` - Audio info
• `{video}` - Video info
• `{resolution}` - Video resolution
• `{codec}` - Video codec
• `{duration}` - File duration
• `{size}` - File size

**Examples:**
• `{title} - {artist}` → "Song - Artist"
• `[{year}] {title}` → "[2023] Movie"
• `{title} ({resolution})` → "Video (1080p)"

Choose an option below:
        """
        
        await update.message.reply_text(
            format_help,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.format_menu()
        )
    
    async def getfmt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /getfmt command to show current format."""
        user_id = update.effective_user.id
        user_data = self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found. Please start the bot first with /start")
            return
        
        current_format = user_data.get('format_template', '{title}')
        
        await update.message.reply_text(
            f"📝 **Current Format Template:**\n\n`{current_format}`\n\nUse /format to change it.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command to clear processing queue."""
        user_id = update.effective_user.id
        
        # Clear user's processing state
        if user_id in self.processing_files:
            del self.processing_files[user_id]
        
        if user_id in self.user_states:
            del self.user_states[user_id]
        
        await update.message.reply_text(
            "🗑️ **Queue Cleared**\n\nAll pending files and states have been cleared.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def set_media_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /set_media command for media type selection."""
        await update.message.reply_text(
            "📁 **Select Media Type**\n\n**Document:** Files sent as documents (default)\n\n**Video:** Files sent as videos (with video player)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.media_type_menu()
        )
    
    async def metadata_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /metadata command for metadata management."""
        user_id = update.effective_user.id
        user_data = self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found. Please start the bot first with /start")
            return
        
        metadata_status = "On" if user_data.get('auto_metadata', True) else "Off"
        
        metadata_text = f"""
🎯 **Your Metadata is currently: {metadata_status}**

🔹 **Title** ▸ @ANIME_NEXUUS
🔹 **Author** ▸ @ANIME_NEXUUS  
🔹 **Artist** ▸ @ANIME_NEXUUS
🔹 **Audio** ▸ @ANIME_NEXUUS
🔹 **Subtitle** ▸ @ANIME_NEXUUS
🔹 **Video** ▸ @ANIME_NEXUUS
        """
        
        # Create inline keyboard for metadata toggle
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("On ✅", callback_data="metadata_on"),
                InlineKeyboardButton("Off", callback_data="metadata_off")
            ],
            [InlineKeyboardButton("How to Set Metadata", callback_data="metadata_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            metadata_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def mode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /mode command for rename mode selection."""
        await update.message.reply_text(
            "🔄 **Select Rename Mode**\n\n**Auto Mode:** Files are renamed automatically using your format template.\n\n**Manual Mode:** You'll be asked to enter a filename for each file.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.rename_mode_menu()
        )
    
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming files for renaming."""
        user_id = update.effective_user.id
        
        # Check rate limiting
        if not self.db.check_rate_limit(user_id):
            await update.message.reply_text(
                "⏳ Please wait before sending another file. Rate limit exceeded."
            )
            return
        
        # Check if user is banned
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        # Add user if not exists
        user = update.effective_user
        self.db.add_user(user_id, user.username, user.first_name, user.last_name)
        
        # Get file object
        file_obj = None
        if update.message.document:
            file_obj = update.message.document
            file_type = "document"
        elif update.message.video:
            file_obj = update.message.video
            file_type = "video"
        else:
            await update.message.reply_text("❌ Unsupported file type.")
            return
        
        # Check file size
        if file_obj.file_size > self.config.MAX_FILE_SIZE:
            size_limit = FileUtils.format_file_size(self.config.MAX_FILE_SIZE)
            await update.message.reply_text(
                f"❌ File too large. Maximum size allowed: {size_limit}"
            )
            return
        
        # Get user settings
        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ User data not found. Please use /start first.")
            return
        
        # Check rename mode
        rename_mode = user_data.get('rename_mode', 'auto')
        
        if rename_mode == 'manual':
            # Store file for manual processing
            self.user_states[user_id] = {
                'action': 'awaiting_filename',
                'file_obj': file_obj,
                'file_type': file_type,
                'message_id': update.message.message_id
            }
            
            await update.message.reply_text(
                "📝 **Manual Mode**\n\nPlease send the new filename for this file:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.file_options(str(file_obj.file_id))
            )
        else:
            # Auto mode - process immediately
            await self.process_file_auto(update, context, file_obj, file_type, user_data)
    
    async def process_file_auto(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                               file_obj, file_type: str, user_data: Dict) -> None:
        """Process file in automatic mode."""
        user_id = update.effective_user.id
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔄 **Processing file...**\n\n⏳ Downloading file...",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.processing_status()
        )
        
        try:
            # Mark as processing
            self.processing_files[user_id] = {
                'active': True,
                'message': processing_msg,
                'start_time': time.time()
            }
            
            # Process the file
            result = await self.file_manager.process_file(
                file_obj, file_type, user_data, 
                progress_callback=lambda msg: self.update_progress(processing_msg, msg)
            )
            
            if result['success']:
                # Update final message
                final_text = f"""
✅ **File Renamed Successfully!**

**Original:** `{result['original_name']}`
**New Name:** `{result['new_name']}`
**Size:** {FileUtils.format_file_size(result['file_size'])}
**Processing Time:** {result['processing_time']:.1f}s

File has been sent below ⬇️
                """
                
                await processing_msg.edit_text(
                    final_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboards.close_message()
                )
                
                # Send the renamed file
                await self.send_renamed_file(update, context, result, user_data)
                
                # Forward to dump channels if configured
                await self.forward_to_dump_channels(context, result['file_path'], result['new_name'])
                
            else:
                await processing_msg.edit_text(
                    f"❌ **Processing Failed**\n\n{result['error']}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboards.close_message()
                )
        
        except Exception as e:
            logger.error(f"Error processing file for user {user_id}: {e}")
            await processing_msg.edit_text(
                "❌ **Processing Failed**\n\nAn unexpected error occurred. Please try again.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        
        finally:
            # Remove from processing
            self.processing_files.pop(user_id, None)
    
    async def update_progress(self, message: Message, progress_text: str) -> None:
        """Update progress message."""
        try:
            await message.edit_text(
                f"🔄 **Processing file...**\n\n{progress_text}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.processing_status()
            )
        except TelegramError:
            # Ignore edit errors (message not modified, etc.)
            pass
    
    async def send_renamed_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                               result: Dict, user_data: Dict) -> None:
        """Send the renamed file to user."""
        try:
            media_type = user_data.get('media_type', 'document')
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.UPLOAD_DOCUMENT if media_type == 'document' else ChatAction.UPLOAD_VIDEO
            )
            
            with open(result['file_path'], 'rb') as file:
                if media_type == 'document':
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=file,
                        filename=result['new_name'],
                        caption=f"📁 **Renamed File**\n\n`{result['new_name']}`",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=file,
                        filename=result['new_name'],
                        caption=f"🎥 **Renamed Video**\n\n`{result['new_name']}`",
                        parse_mode=ParseMode.MARKDOWN
                    )
        
        except Exception as e:
            logger.error(f"Error sending renamed file: {e}")
            await update.message.reply_text(
                "❌ Error sending renamed file. The file was processed but couldn't be sent."
            )
    
    async def forward_to_dump_channels(self, context: ContextTypes.DEFAULT_TYPE,
                                     file_path: str, filename: str) -> None:
        """Forward renamed file to dump channels."""
        try:
            dump_channels = self.db.get_dump_channels()
            
            for channel in dump_channels:
                channel_id = channel['channel_id']
                
                try:
                    with open(file_path, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=channel_id,
                            document=file,
                            filename=filename,
                            caption=f"📁 Auto-forwarded: `{filename}`",
                            parse_mode=ParseMode.MARKDOWN
                        )
                except Exception as e:
                    logger.warning(f"Failed to forward to channel {channel_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error forwarding to dump channels: {e}")
    
    async def handle_thumbnail(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle thumbnail images."""
        user_id = update.effective_user.id
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        # Check if user is in thumbnail setting mode
        user_state = self.user_states.get(user_id, {})
        if user_state.get('action') == 'awaiting_thumbnail':
            # Save thumbnail for later use
            photo = update.message.photo[-1]  # Get highest resolution
            
            # Store thumbnail info
            self.user_states[user_id]['thumbnail'] = {
                'file_id': photo.file_id,
                'width': photo.width,
                'height': photo.height
            }
            
            await update.message.reply_text(
                "✅ **Thumbnail saved!**\n\nThis thumbnail will be used for your next video file.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
            
            # Clear state
            self.user_states.pop(user_id, None)
        else:
            await update.message.reply_text(
                "🖼️ **Thumbnail received**\n\nUse the thumbnail menu to manage thumbnails.",
                reply_markup=self.keyboards.thumbnail_menu()
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages based on user state."""
        user_id = update.effective_user.id
        text = update.message.text
        
        if self.db.is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        
        user_state = self.user_states.get(user_id, {})
        action = user_state.get('action')
        
        if action == 'awaiting_filename':
            # Handle manual filename input
            await self.handle_manual_filename(update, context, text)
        
        elif action == 'awaiting_format':
            # Handle custom format input
            await self.handle_custom_format(update, context, text)
        
        elif action == 'awaiting_broadcast':
            # Handle broadcast message (admin only)
            if self.db.is_admin(user_id) or self.config.is_owner(user_id):
                await self.handle_broadcast_message(update, context, text)
            else:
                await update.message.reply_text("❌ You don't have permission to broadcast.")
        
        else:
            # Default response for unrecognized text
            await update.message.reply_text(
                "🤖 I didn't understand that. Use /help to see available commands.",
                reply_markup=self.keyboards.main_menu()
            )
    
    async def handle_manual_filename(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filename: str) -> None:
        """Handle manual filename input."""
        user_id = update.effective_user.id
        user_state = self.user_states.get(user_id, {})
        
        if not user_state or 'file_obj' not in user_state:
            await update.message.reply_text("❌ No file to rename. Please send a file first.")
            return
        
        # Clean the filename
        clean_filename = FileUtils.clean_filename(filename)
        if not clean_filename:
            await update.message.reply_text("❌ Invalid filename. Please try again.")
            return
        
        # Get user data
        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ User data not found.")
            return
        
        # Process file with manual filename
        file_obj = user_state['file_obj']
        file_type = user_state['file_type']
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔄 **Processing file with custom name...**\n\n⏳ Starting process...",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.processing_status()
        )
        
        try:
            # Mark as processing
            self.processing_files[user_id] = {
                'active': True,
                'message': processing_msg,
                'start_time': time.time()
            }
            
            # Process with custom filename
            result = await self.file_manager.process_file_with_name(
                file_obj, file_type, clean_filename, user_data,
                progress_callback=lambda msg: self.update_progress(processing_msg, msg)
            )
            
            if result['success']:
                # Update success message
                final_text = f"""
✅ **File Renamed Successfully!**

**Original:** `{result['original_name']}`
**New Name:** `{result['new_name']}`
**Size:** {FileUtils.format_file_size(result['file_size'])}
**Processing Time:** {result['processing_time']:.1f}s

File has been sent below ⬇️
                """
                
                await processing_msg.edit_text(
                    final_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboards.close_message()
                )
                
                # Send the renamed file
                await self.send_renamed_file(update, context, result, user_data)
                
                # Forward to dump channels
                await self.forward_to_dump_channels(context, result['file_path'], result['new_name'])
            
            else:
                await processing_msg.edit_text(
                    f"❌ **Processing Failed**\n\n{result['error']}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboards.close_message()
                )
        
        except Exception as e:
            logger.error(f"Error in manual filename processing: {e}")
            await processing_msg.edit_text(
                "❌ **Processing Failed**\n\nAn unexpected error occurred.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        
        finally:
            # Clear user state and processing
            self.user_states.pop(user_id, None)
            self.processing_files.pop(user_id, None)
    
    async def handle_custom_format(self, update: Update, context: ContextTypes.DEFAULT_TYPE, format_text: str) -> None:
        """Handle custom format template input."""
        user_id = update.effective_user.id
        
        # Validate format template
        is_valid, error_msg = TextUtils.is_valid_format_template(format_text)
        
        if not is_valid:
            await update.message.reply_text(f"❌ **Invalid Format Template**\n\n{error_msg}")
            return
        
        # Update user format
        success = self.db.update_user_settings(user_id, custom_format=format_text)
        
        if success:
            await update.message.reply_text(
                f"✅ **Format Updated!**\n\nNew format: `{format_text}`\n\nThis will be used for auto-renaming files.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        else:
            await update.message.reply_text("❌ Failed to update format. Please try again.")
        
        # Clear user state
        self.user_states.pop(user_id, None)
    
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
        """Handle broadcast message from admin."""
        user_id = update.effective_user.id
        
        # Send confirmation
        await update.message.reply_text(
            f"📢 **Broadcasting message:**\n\n{message}\n\nStarting broadcast...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Get all users
        all_users = self.db.get_all_users()
        success_count = 0
        failed_count = 0
        
        # Broadcast to all users
        for target_user_id in all_users:
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"📢 **Broadcast Message**\n\n{message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                success_count += 1
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Failed to send broadcast to {target_user_id}: {e}")
                failed_count += 1
        
        # Send result
        result_text = f"""
📢 **Broadcast Complete**

**Total Users:** {len(all_users)}
**Successful:** {success_count}
**Failed:** {failed_count}
        """
        
        await update.message.reply_text(
            result_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )
        
        # Clear user state
        self.user_states.pop(user_id, None)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all inline keyboard button callbacks."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Check if user is banned
        if self.db.is_banned(user_id):
            await query.edit_message_text("❌ You are banned from using this bot.")
            return
        
        # Route to appropriate handler based on callback data
        if data == "main_menu":
            await self.show_main_menu(query)
        elif data == "settings":
            await self.show_settings(query)
        elif data == "stats":
            await self.show_user_stats(query)
        elif data == "format":
            await self.show_format_menu(query)
        elif data == "thumbnail":
            await self.show_thumbnail_menu(query)
        elif data == "help":
            await self.show_help(query)
        elif data == "leaderboard":
            await self.show_leaderboard(query)
        elif data.startswith("set_"):
            await self.handle_setting_change(query, data)
        elif data.startswith("mode_"):
            await self.handle_mode_change(query, data)
        elif data.startswith("type_"):
            await self.handle_type_change(query, data)
        elif data.startswith("format_"):
            await self.handle_format_action(query, data)
        elif data.startswith("thumb_"):
            await self.handle_thumbnail_action(query, data)
        elif data == "close_message":
            await query.delete_message()
        else:
            await query.edit_message_text("❌ Unknown action.")
    
    async def show_main_menu(self, query) -> None:
        """Show main menu."""
        user = query.from_user
        text = f"""
🤖 **Auto-Rename Bot - Main Menu**

Welcome back, {user.first_name}!

Choose an option below:
        """
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.main_menu()
        )
    
    async def show_settings(self, query) -> None:
        """Show settings menu."""
        user_id = query.from_user.id
        user_data = self.db.get_user(user_id)
        
        if not user_data:
            await query.edit_message_text("❌ User data not found. Please use /start first.")
            return
        
        settings_text = f"""
⚙️ **Your Current Settings**

**Rename Mode:** {user_data.get('rename_mode', 'auto').title()}
**Media Type:** {user_data.get('media_type', 'document').title()}
**Custom Format:** `{user_data.get('custom_format', '{title}')}`
**Auto Thumbnail:** {'✅ Enabled' if user_data.get('auto_thumbnail') else '❌ Disabled'}

Choose a setting to modify:
        """
        
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.settings_menu()
        )
    
    async def show_user_stats(self, query) -> None:
        """Show user statistics."""
        user_id = query.from_user.id
        stats = self.db.get_user_stats(user_id)
        
        if not stats:
            await query.edit_message_text("❌ No statistics available.")
            return
        
        stats_text = f"""
📊 **Your Statistics**

**Files Renamed:** {stats.get('files_renamed', 0)}
**Total Size Processed:** {FileUtils.format_file_size(stats.get('total_size', 0))}
**Member Since:** {stats.get('join_date', 'Unknown')}
**Last Activity:** {stats.get('last_activity', 'Unknown')}
**Recent Files (7 days):** {stats.get('recent_files', 0)}

Keep using the bot to improve your stats! 📈
        """
        
        await query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )
    
    async def show_format_menu(self, query) -> None:
        """Show format template menu."""
        format_help = """
📝 **Format Template Guide**

**Available Variables:**
• `{title}` - File title/name
• `{author}` - Author name
• `{artist}` - Artist name
• `{album}` - Album name
• `{genre}` - Genre
• `{year}` - Year
• `{audio}` - Audio info
• `{video}` - Video info
• `{resolution}` - Video resolution
• `{codec}` - Video codec
• `{duration}` - File duration
• `{size}` - File size

**Examples:**
• `{title} - {artist}` → "Song - Artist"
• `[{year}] {title}` → "[2023] Movie"
• `{title} ({resolution})` → "Video (1080p)"

Choose an option below:
        """
        
        await query.edit_message_text(
            format_help,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.format_menu()
        )
    
    async def show_thumbnail_menu(self, query) -> None:
        """Show thumbnail management menu."""
        thumbnail_text = """
🖼️ **Thumbnail Management**

Manage thumbnails for your video files:

• **Extract from Video** - Get thumbnail from video frame
• **Set Custom** - Upload your own thumbnail image
• **Save Current** - Save current thumbnail for reuse
• **Delete** - Remove saved thumbnail

Choose an option:
        """
        
        await query.edit_message_text(
            thumbnail_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.thumbnail_menu()
        )
    
    async def show_help(self, query) -> None:
        """Show help information."""
        await query.edit_message_text(
            self.config.get_help_text(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )
    
    async def show_leaderboard(self, query) -> None:
        """Show user leaderboard."""
        leaderboard = self.db.get_leaderboard(10)
        
        if not leaderboard:
            await query.edit_message_text(
                "🏆 **Leaderboard**\n\nNo users found yet. Be the first to rename a file!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
            return
        
        leaderboard_text = "🏆 **Top Users - Files Renamed**\n\n"
        
        for i, user in enumerate(leaderboard, 1):
            username = user.get('username', 'Unknown')
            first_name = user.get('first_name', 'User')
            files_count = user.get('files_renamed', 0)
            total_size = FileUtils.format_file_size(user.get('total_size', 0))
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            leaderboard_text += f"{medal} **{first_name}**"
            if username:
                leaderboard_text += f" (@{username})"
            leaderboard_text += f"\n    Files: {files_count} | Size: {total_size}\n\n"
        
        await query.edit_message_text(
            leaderboard_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.close_message()
        )
    
    async def handle_setting_change(self, query, data: str) -> None:
        """Handle setting changes."""
        if data == "set_rename_mode":
            await query.edit_message_text(
                "🔄 **Select Rename Mode**\n\n**Auto Mode:** Files are renamed automatically using your format template.\n\n**Manual Mode:** You'll be asked to enter a filename for each file.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.rename_mode_menu()
            )
        elif data == "set_media_type":
            await query.edit_message_text(
                "📁 **Select Media Type**\n\n**Document:** Files sent as documents (default)\n\n**Video:** Files sent as videos (with video player)",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.media_type_menu()
            )
        elif data == "toggle_auto_thumb":
            user_id = query.from_user.id
            user_data = self.db.get_user(user_id)
            current_setting = user_data.get('auto_thumbnail', True)
            new_setting = not current_setting
            
            success = self.db.update_user_settings(user_id, auto_thumbnail=new_setting)
            
            if success:
                status = "✅ Enabled" if new_setting else "❌ Disabled"
                await query.edit_message_text(
                    f"🖼️ **Auto Thumbnail {status}**\n\nThumbnails will {'automatically be extracted from videos' if new_setting else 'not be set automatically'}.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboards.close_message()
                )
            else:
                await query.edit_message_text("❌ Failed to update setting.")
        elif data == "set_format":
            self.user_states[query.from_user.id] = {'action': 'awaiting_format'}
            await query.edit_message_text(
                "📝 **Enter Custom Format Template**\n\nSend your custom format template using the available variables.\n\nExample: `{title} - {artist}`",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_mode_change(self, query, data: str) -> None:
        """Handle rename mode changes."""
        user_id = query.from_user.id
        mode = data.replace("mode_", "")
        
        success = self.db.update_user_settings(user_id, rename_mode=mode)
        
        if success:
            mode_text = "🤖 **Auto Mode**" if mode == "auto" else "✋ **Manual Mode**"
            description = "Files will be renamed automatically using your format template." if mode == "auto" else "You'll be asked to enter a filename for each file."
            
            await query.edit_message_text(
                f"{mode_text} **Selected**\n\n{description}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        else:
            await query.edit_message_text("❌ Failed to update rename mode.")
    
    async def handle_type_change(self, query, data: str) -> None:
        """Handle media type changes."""
        user_id = query.from_user.id
        media_type = data.replace("type_", "")
        
        success = self.db.update_user_settings(user_id, media_type=media_type)
        
        if success:
            type_text = "📄 **Document**" if media_type == "document" else "🎥 **Video**"
            description = "Files will be sent as documents." if media_type == "document" else "Files will be sent as videos with video player."
            
            await query.edit_message_text(
                f"{type_text} **Selected**\n\n{description}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        else:
            await query.edit_message_text("❌ Failed to update media type.")
    
    async def handle_format_action(self, query, data: str) -> None:
        """Handle format-related actions."""
        if data == "format_custom":
            self.user_states[query.from_user.id] = {'action': 'awaiting_format'}
            await query.edit_message_text(
                "📝 **Enter Custom Format Template**\n\nSend your custom format template using the available variables.\n\nExample: `{title} - {artist}`",
                parse_mode=ParseMode.MARKDOWN
            )
        elif data == "format_help":
            await self.show_format_menu(query)
        elif data == "format_reset":
            user_id = query.from_user.id
            success = self.db.update_user_settings(user_id, custom_format=self.config.DEFAULT_FORMAT)
            
            if success:
                await query.edit_message_text(
                    f"🔄 **Format Reset**\n\nFormat has been reset to default: `{self.config.DEFAULT_FORMAT}`",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.keyboards.close_message()
                )
            else:
                await query.edit_message_text("❌ Failed to reset format.")
    
    async def handle_thumbnail_action(self, query, data: str) -> None:
        """Handle thumbnail-related actions."""
        user_id = query.from_user.id
        
        if data == "thumb_custom":
            self.user_states[user_id] = {'action': 'awaiting_thumbnail'}
            await query.edit_message_text(
                "🖼️ **Send Thumbnail Image**\n\nSend a photo to use as thumbnail for your next video file.",
                parse_mode=ParseMode.MARKDOWN
            )
        elif data == "thumb_extract":
            await query.edit_message_text(
                "📤 **Extract Thumbnail**\n\nSend a video file and I'll extract a thumbnail from it.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        elif data == "thumb_save":
            await query.edit_message_text(
                "💾 **Save Thumbnail**\n\nFeature coming soon! You'll be able to save thumbnails for reuse.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
        elif data == "thumb_delete":
            # Clear saved thumbnail
            self.user_states.pop(user_id, None)
            await query.edit_message_text(
                "🗑️ **Thumbnail Deleted**\n\nSaved thumbnail has been removed.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.keyboards.close_message()
            )
