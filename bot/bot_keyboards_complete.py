"""
Complete bot/keyboards.py file content for GitHub upload
Copy this entire content to your bot/keyboards.py file
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

class BotKeyboards:
    """Class containing all inline keyboard layouts for the bot."""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("📊 Statistics", callback_data="stats")
            ],
            [
                InlineKeyboardButton("📝 Format", callback_data="format"),
                InlineKeyboardButton("🖼️ Thumbnails", callback_data="thumbnails")
            ],
            [
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🔄 Rename Mode", callback_data="setting_rename_mode"),
                InlineKeyboardButton("📁 Media Type", callback_data="setting_media_type")
            ],
            [
                InlineKeyboardButton("📝 Custom Format", callback_data="setting_custom_format"),
                InlineKeyboardButton("🖼️ Auto Thumbnail", callback_data="setting_auto_thumbnail")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def rename_mode_menu() -> InlineKeyboardMarkup:
        """Rename mode selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🤖 Auto Mode", callback_data="mode_auto"),
                InlineKeyboardButton("✏️ Manual Mode", callback_data="mode_manual")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def media_type_menu() -> InlineKeyboardMarkup:
        """Media type selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📄 Document", callback_data="type_document"),
                InlineKeyboardButton("🎥 Video", callback_data="type_video")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def thumbnail_menu() -> InlineKeyboardMarkup:
        """Thumbnail management keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📤 Extract", callback_data="thumb_extract"),
                InlineKeyboardButton("🔄 Change", callback_data="thumb_change")
            ],
            [
                InlineKeyboardButton("🗑️ Delete", callback_data="thumb_delete"),
                InlineKeyboardButton("💾 Save", callback_data="thumb_save")
            ],
            [
                InlineKeyboardButton("🎭 Steal", callback_data="thumb_steal"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_menu() -> InlineKeyboardMarkup:
        """Format template menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Custom Format", callback_data="format_custom"),
                InlineKeyboardButton("📋 Examples", callback_data="format_examples")
            ],
            [
                InlineKeyboardButton("🔄 Reset Default", callback_data="format_reset"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin control menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("📁 Dump Channels", callback_data="admin_dumps")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, data: str = "") -> InlineKeyboardMarkup:
        """Confirmation keyboard for actions."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{data}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def file_options(file_id: str) -> InlineKeyboardMarkup:
        """File processing options keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🤖 Auto Rename", callback_data=f"auto_{file_id}"),
                InlineKeyboardButton("✏️ Manual Rename", callback_data=f"manual_{file_id}")
            ],
            [
                InlineKeyboardButton("🖼️ Set Thumbnail", callback_data=f"thumb_{file_id}"),
                InlineKeyboardButton("📝 Edit Metadata", callback_data=f"meta_{file_id}")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def processing_status() -> InlineKeyboardMarkup:
        """Processing status keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_processing")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Pagination keyboard."""
        keyboard = []
        
        # Navigation buttons
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{prefix}_page_{current_page-1}"))
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{prefix}_page_{current_page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Page info
        keyboard.append([
            InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="page_info")
        ])
        
        # Close button
        keyboard.append([
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def yes_no(action: str) -> InlineKeyboardMarkup:
        """Simple Yes/No keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"yes_{action}"),
                InlineKeyboardButton("❌ No", callback_data=f"no_{action}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_templates(templates: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Format templates selection keyboard."""
        keyboard = []
        
        # Template buttons (2 per row)
        for i in range(0, len(templates), 2):
            row = []
            for j in range(i, min(i + 2, len(templates))):
                template = templates[j]
                row.append(InlineKeyboardButton(
                    template['name'], 
                    callback_data=f"template_{template['id']}"
                ))
            keyboard.append(row)
        
        # Control buttons
        keyboard.append([
            InlineKeyboardButton("➕ Add New", callback_data="template_add"),
            InlineKeyboardButton("🗑️ Delete", callback_data="template_delete")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data="format"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def dump_channels(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Dump channels management keyboard."""
        keyboard = []
        
        # Channel buttons
        for channel in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"📁 {channel['channel_name']}", 
                    callback_data=f"dump_view_{channel['channel_id']}"
                ),
                InlineKeyboardButton(
                    "🗑️", 
                    callback_data=f"dump_remove_{channel['channel_id']}"
                )
            ])
        
        # Control buttons
        keyboard.append([
            InlineKeyboardButton("➕ Add Channel", callback_data="dump_add"),
            InlineKeyboardButton("📊 Statistics", callback_data="dump_stats")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data="admin_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def user_management() -> InlineKeyboardMarkup:
        """User management keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🚫 Ban User", callback_data="user_ban"),
                InlineKeyboardButton("✅ Unban User", callback_data="user_unban")
            ],
            [
                InlineKeyboardButton("👑 Make Admin", callback_data="user_make_admin"),
                InlineKeyboardButton("👤 Remove Admin", callback_data="user_remove_admin")
            ],
            [
                InlineKeyboardButton("📊 User Stats", callback_data="user_stats"),
                InlineKeyboardButton("📋 User List", callback_data="user_list")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="admin_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def close_message() -> InlineKeyboardMarkup:
        """Close message keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)