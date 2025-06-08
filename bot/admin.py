"""
Complete bot/admin.py file content for GitHub upload
Copy this entire content to your bot/admin.py file
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

from .database import Database
from .keyboards import BotKeyboards
from config import Config

logger = logging.getLogger(__name__)

class AdminHandlers:
    """Handlers for admin-only functionality."""
    
    def __init__(self, database: Database):
        """Initialize admin handlers with database connection."""
        self.db = database
        self.config = Config()
        self.keyboards = BotKeyboards()
        self.admin_states = {}  # Store admin conversation states
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized for admin actions."""
        return (self.config.is_owner(user_id) or self.db.is_admin(user_id)) and not self.db.is_banned(user_id)
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /broadcast command for sending messages to all users."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        
        # Check if message provided
        if context.args:
            message = " ".join(context.args)
            await self.send_broadcast(update, context, message)
        else:
            # Set state for broadcast message input
            self.admin_states[user_id] = {'state': 'waiting_broadcast'}
            await update.message.reply_text(
                "📢 **Broadcast Message**\n\nSend the message you want to broadcast to all users:",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def send_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
        """Send broadcast message to all users."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized for this action.")
            return
        
        # Get all users
        all_users = self.db.get_all_users()
        
        if not all_users:
            await update.message.reply_text("❌ No users found to broadcast to.")
            return
        
        # Send broadcast
        progress_msg = await update.message.reply_text(f"📢 Broadcasting to {len(all_users)} users...")
        
        success_count = 0
        failed_count = 0
        
        broadcast_text = f"📢 **Broadcast Message**\n\n{message}\n\n— Bot Admin"
        
        for target_user_id in all_users:
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=broadcast_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                success_count += 1
                
                # Update progress every 10 users
                if success_count % 10 == 0:
                    try:
                        await progress_msg.edit_text(
                            f"📢 Broadcasting... {success_count}/{len(all_users)} sent"
                        )
                    except:
                        pass
                        
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except TelegramError as e:
                failed_count += 1
                logger.warning(f"Failed to send broadcast to {target_user_id}: {e}")
        
        # Final result
        result_text = f"""
✅ **Broadcast Complete**

**Successfully sent:** {success_count}
**Failed:** {failed_count}
**Total users:** {len(all_users)}

Message: "{message[:50]}{'...' if len(message) > 50 else ''}"
        """
        
        await progress_msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
        
        # Clear admin state
        if user_id in self.admin_states:
            del self.admin_states[user_id]
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /ban command for banning users."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: `/ban <user_id>`\n\nExample: `/ban 123456789`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            target_user_id = int(context.args[0])
            
            # Prevent banning the owner
            if self.config.is_owner(target_user_id):
                await update.message.reply_text("❌ Cannot ban the bot owner.")
                return
            
            # Prevent banning self
            if target_user_id == user_id:
                await update.message.reply_text("❌ Cannot ban yourself.")
                return
            
            if self.db.ban_user(target_user_id):
                await update.message.reply_text(f"✅ User {target_user_id} has been banned.")
                
                # Notify the banned user
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="❌ You have been banned from using this bot."
                    )
                except:
                    pass  # User might have blocked the bot
            else:
                await update.message.reply_text("❌ Failed to ban user.")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Use a numeric ID.")
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            await update.message.reply_text("❌ An error occurred while banning the user.")
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /unban command for unbanning users."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: `/unban <user_id>`\n\nExample: `/unban 123456789`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            target_user_id = int(context.args[0])
            
            if self.db.unban_user(target_user_id):
                await update.message.reply_text(f"✅ User {target_user_id} has been unbanned.")
                
                # Notify the unbanned user
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="✅ You have been unbanned and can now use the bot again."
                    )
                except:
                    pass  # User might have blocked the bot
            else:
                await update.message.reply_text("❌ Failed to unban user.")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Use a numeric ID.")
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            await update.message.reply_text("❌ An error occurred while unbanning the user.")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /admin command for managing admin status."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        # Only owner can manage admins
        if not self.config.is_owner(user_id):
            await update.message.reply_text("❌ Only the bot owner can manage admin status.")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: `/admin <add|remove> <user_id>`\n\n"
                "Examples:\n"
                "• `/admin add 123456789`\n"
                "• `/admin remove 123456789`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        action = context.args[0].lower()
        
        try:
            target_user_id = int(context.args[1])
            
            if action == "add":
                if self.db.set_admin(target_user_id, True):
                    await update.message.reply_text(f"✅ User {target_user_id} has been promoted to admin.")
                    
                    # Notify the new admin
                    try:
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text="🎉 You have been promoted to admin! You now have access to admin commands."
                        )
                    except:
                        pass
                else:
                    await update.message.reply_text("❌ Failed to promote user to admin.")
                    
            elif action == "remove":
                if target_user_id == user_id:
                    await update.message.reply_text("❌ Cannot remove admin status from yourself.")
                    return
                
                if self.db.set_admin(target_user_id, False):
                    await update.message.reply_text(f"✅ Admin status removed from user {target_user_id}.")
                    
                    # Notify the demoted admin
                    try:
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text="📝 Your admin status has been removed."
                        )
                    except:
                        pass
                else:
                    await update.message.reply_text("❌ Failed to remove admin status.")
            else:
                await update.message.reply_text("❌ Invalid action. Use 'add' or 'remove'.")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Use a numeric ID.")
        except Exception as e:
            logger.error(f"Error managing admin status: {e}")
            await update.message.reply_text("❌ An error occurred while managing admin status.")
    
    async def dump_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /dump command for managing dump channels."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "**Dump Channel Management**\n\n"
                "Usage:\n"
                "• `/dump add <channel_id>` - Add dump channel\n"
                "• `/dump remove <channel_id>` - Remove dump channel\n"
                "• `/dump list` - List all dump channels\n\n"
                "Example: `/dump add -1001234567890`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        action = context.args[0].lower()
        
        if action == "add":
            if len(context.args) < 2:
                await update.message.reply_text("❌ Please provide a channel ID.")
                return
            
            try:
                channel_id = int(context.args[1])
                await self.add_dump_channel(update, context, channel_id)
            except ValueError:
                await update.message.reply_text("❌ Invalid channel ID. Use a numeric ID.")
                
        elif action == "remove":
            if len(context.args) < 2:
                await update.message.reply_text("❌ Please provide a channel ID.")
                return
            
            try:
                channel_id = int(context.args[1])
                await self.remove_dump_channel(update, channel_id)
            except ValueError:
                await update.message.reply_text("❌ Invalid channel ID. Use a numeric ID.")
                
        elif action == "list":
            await self.list_dump_channels(update)
        else:
            await update.message.reply_text("❌ Invalid action. Use 'add', 'remove', or 'list'.")
    
    async def add_dump_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: int) -> None:
        """Add a dump channel."""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        
        try:
            # Try to get channel info
            chat = await context.bot.get_chat(channel_id)
            channel_name = chat.title or f"Channel {channel_id}"
            
            # Check if bot is admin in the channel
            bot_member = await context.bot.get_chat_member(channel_id, context.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                await update.message.reply_text(
                    "❌ Bot must be an administrator in the channel to use it as a dump channel."
                )
                return
            
            if self.db.add_dump_channel(channel_id, channel_name, user_id):
                await update.message.reply_text(
                    f"✅ Dump channel added successfully!\n\n"
                    f"**Channel:** {channel_name}\n"
                    f"**ID:** `{channel_id}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text("❌ Channel already exists or failed to add.")
                
        except TelegramError as e:
            if "chat not found" in str(e).lower():
                await update.message.reply_text("❌ Channel not found. Make sure the channel ID is correct.")
            elif "not enough rights" in str(e).lower():
                await update.message.reply_text("❌ Bot doesn't have permission to access this channel.")
            else:
                await update.message.reply_text(f"❌ Error accessing channel: {e}")
        except Exception as e:
            logger.error(f"Error adding dump channel: {e}")
            await update.message.reply_text("❌ An error occurred while adding the dump channel.")
    
    async def remove_dump_channel(self, update: Update, channel_id: int) -> None:
        """Remove a dump channel."""
        if not update.message:
            return
        
        if self.db.remove_dump_channel(channel_id):
            await update.message.reply_text(f"✅ Dump channel {channel_id} removed successfully.")
        else:
            await update.message.reply_text("❌ Channel not found or failed to remove.")
    
    async def list_dump_channels(self, update: Update) -> None:
        """List all dump channels."""
        if not update.message:
            return
        
        channels = self.db.get_dump_channels()
        
        if not channels:
            await update.message.reply_text("📁 No dump channels configured.")
            return
        
        channels_text = "📁 **Active Dump Channels:**\n\n"
        
        for i, channel in enumerate(channels, 1):
            channels_text += f"{i}. **{channel['channel_name']}**\n"
            channels_text += f"   ID: `{channel['channel_id']}`\n"
            channels_text += f"   Added: {channel['added_date']}\n\n"
        
        await update.message.reply_text(channels_text, parse_mode=ParseMode.MARKDOWN)
    
    async def get_bot_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics."""
        try:
            conn = self.db.get_connection()
            
            # Total users
            total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
            
            # Active users (last 7 days)
            active_users = conn.execute("""
                SELECT COUNT(*) as count FROM users 
                WHERE last_activity > datetime('now', '-7 days')
            """).fetchone()['count']
            
            # Total files processed
            total_files = conn.execute("SELECT COUNT(*) as count FROM file_history").fetchone()['count']
            
            # Total data processed
            total_size = conn.execute("SELECT SUM(file_size) as size FROM file_history").fetchone()['size'] or 0
            
            # Files today
            files_today = conn.execute("""
                SELECT COUNT(*) as count FROM file_history 
                WHERE processed_date > date('now')
            """).fetchone()['count']
            
            # Banned users
            banned_users = conn.execute("SELECT COUNT(*) as count FROM users WHERE is_banned = 1").fetchone()['count']
            
            # Admin users
            admin_users = conn.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = 1").fetchone()['count']
            
            # Dump channels
            dump_channels = conn.execute("SELECT COUNT(*) as count FROM dump_channels WHERE is_active = 1").fetchone()['count']
            
            conn.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_files': total_files,
                'total_size': total_size,
                'files_today': files_today,
                'banned_users': banned_users,
                'admin_users': admin_users,
                'dump_channels': dump_channels
            }
            
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {}
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle admin-specific callback queries."""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        
        if not self.is_authorized(user_id):
            await query.answer("❌ You are not authorized for admin actions.")
            return
        
        try:
            await query.answer()
            
            if data == "admin_menu":
                await self.show_admin_menu(query)
            elif data == "admin_stats":
                await self.show_admin_stats(query)
            elif data == "admin_users":
                await self.show_user_management(query)
            elif data == "admin_dumps":
                await self.show_dump_management(query)
            elif data == "admin_broadcast":
                await self.prompt_broadcast(query)
            else:
                await query.edit_message_text("❌ Unknown admin action.")
                
        except Exception as e:
            logger.error(f"Error handling admin callback: {e}")
    
    async def show_admin_menu(self, query) -> None:
        """Show admin menu."""
        admin_text = """
🔧 **Admin Control Panel**

Welcome to the admin dashboard. Here you can manage users, channels, and bot settings.

Choose an option below:
        """
        
        await query.edit_message_text(
            admin_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.admin_menu()
        )
    
    async def show_admin_stats(self, query) -> None:
        """Show comprehensive bot statistics."""
        stats = await self.get_bot_stats()
        
        if not stats:
            await query.edit_message_text("❌ Error retrieving statistics.")
            return
        
        from .utils import FileUtils
        
        stats_text = f"""
📊 **Bot Statistics**

**Users:**
• Total Users: {stats.get('total_users', 0)}
• Active (7 days): {stats.get('active_users', 0)}
• Banned Users: {stats.get('banned_users', 0)}
• Admin Users: {stats.get('admin_users', 0)}

**File Processing:**
• Total Files: {stats.get('total_files', 0)}
• Files Today: {stats.get('files_today', 0)}
• Total Data: {FileUtils.format_file_size(stats.get('total_size', 0))}

**Configuration:**
• Dump Channels: {stats.get('dump_channels', 0)}

Last updated: Now
        """
        
        await query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.admin_menu()
        )
    
    async def show_user_management(self, query) -> None:
        """Show user management options."""
        user_text = """
👥 **User Management**

Manage bot users, admins, and bans.

Available actions:
• Ban/Unban users
• Promote/Demote admins
• View user statistics
• List all users

Use the buttons below or commands:
• `/ban <user_id>`
• `/unban <user_id>`
• `/admin add <user_id>`
• `/admin remove <user_id>`
        """
        
        await query.edit_message_text(
            user_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.user_management()
        )
    
    async def show_dump_management(self, query) -> None:
        """Show dump channel management."""
        channels = self.db.get_dump_channels()
        
        dump_text = f"""
📁 **Dump Channel Management**

Active Channels: {len(channels)}

Dump channels automatically receive copies of all processed files.

Commands:
• `/dump add <channel_id>` - Add channel
• `/dump remove <channel_id>` - Remove channel
• `/dump list` - List all channels

Make sure the bot is an admin in the channel before adding it.
        """
        
        await query.edit_message_text(
            dump_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboards.dump_channels(channels)
        )
    
    async def prompt_broadcast(self, query) -> None:
        """Prompt for broadcast message."""
        # Set state for broadcast input
        self.admin_states[query.from_user.id] = {'state': 'waiting_broadcast'}
        
        await query.edit_message_text(
            "📢 **Broadcast Message**\n\n"
            "Send the message you want to broadcast to all users.\n\n"
            "The message will be sent with admin signature.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def get_admin_state(self, user_id: int) -> Dict[str, Any]:
        """Get admin conversation state for user."""
        return self.admin_states.get(user_id, {})
    
    def clear_admin_state(self, user_id: int) -> None:
        """Clear admin conversation state for user."""
        if user_id in self.admin_states:
            del self.admin_states[user_id]
    
    async def handle_admin_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle text input for admin functions. Returns True if handled."""
        if not update.effective_user or not update.message or not update.message.text:
            return False
        
        user_id = update.effective_user.id
        text = update.message.text
        
        if not self.is_authorized(user_id):
            return False
        
        admin_state = self.get_admin_state(user_id)
        
        if admin_state.get('state') == 'waiting_broadcast':
            await self.send_broadcast(update, context, text)
            self.clear_admin_state(user_id)
            return True
        
        return False
