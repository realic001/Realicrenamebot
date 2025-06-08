#!/usr/bin/env python3
"""
Telegram Auto-Rename Bot
A comprehensive file management bot with admin controls and dump channel system.
"""

import logging
import os
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import BotCommand
from config import Config
from bot.handlers import BotHandlers
from bot.admin import AdminHandlers
from bot.database import Database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler('bot.log'),
              logging.StreamHandler()])
logger = logging.getLogger(__name__)


class AutoRenameBot:

    def __init__(self):
        """Initialize the bot with configuration and handlers."""
        self.config = Config()
        self.db = Database()
        self.bot_handlers = BotHandlers(self.db)
        self.admin_handlers = AdminHandlers(self.db)

    async def setup_bot(self):
        """Setup bot with all handlers and configurations."""
        # Create application
        application = Application.builder().token(
            self.config.BOT_TOKEN).build()

        # Command handlers
        application.add_handler(
            CommandHandler("start", self.bot_handlers.start_command))
        application.add_handler(
            CommandHandler("help", self.bot_handlers.help_command))
        application.add_handler(
            CommandHandler("settings", self.bot_handlers.settings_command))
        application.add_handler(
            CommandHandler("stats", self.bot_handlers.stats_command))
        application.add_handler(
            CommandHandler("format", self.bot_handlers.format_command))
        application.add_handler(
            CommandHandler("getfmt", self.bot_handlers.getfmt_command))
        application.add_handler(
            CommandHandler("clear", self.bot_handlers.clear_command))
        application.add_handler(
            CommandHandler("set_media", self.bot_handlers.set_media_command))
        application.add_handler(
            CommandHandler("metadata", self.bot_handlers.metadata_command))
        application.add_handler(
            CommandHandler("mode", self.bot_handlers.mode_command))
        application.add_handler(
            CommandHandler("broadcast", self.admin_handlers.broadcast_command))
        application.add_handler(
            CommandHandler("ban", self.admin_handlers.ban_command))
        application.add_handler(
            CommandHandler("unban", self.admin_handlers.unban_command))
        application.add_handler(
            CommandHandler("admin", self.admin_handlers.admin_command))
        application.add_handler(
            CommandHandler("dump", self.admin_handlers.dump_command))

        # Callback query handler for inline keyboards
        application.add_handler(
            CallbackQueryHandler(self.bot_handlers.button_callback))

        # Message handlers
        application.add_handler(
            MessageHandler(filters.Document.ALL | filters.VIDEO,
                           self.bot_handlers.handle_file))
        application.add_handler(
            MessageHandler(filters.PHOTO, self.bot_handlers.handle_thumbnail))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           self.bot_handlers.handle_text))

        # Error handler
        application.add_error_handler(self.error_handler)

        # Set bot commands menu
        await self.set_bot_commands(application.bot)

        return application

    async def set_bot_commands(self, bot):
        """Set bot commands menu for easy access."""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("format", "Set format template"),
            BotCommand("getfmt", "Get current format"),
            BotCommand("clear", "Clear from queue"),
            BotCommand("set_media", "Select media type"),
            BotCommand("metadata", "For metadata"),
            BotCommand("mode", "Select mode"),
        ]
        
        try:
            await bot.set_my_commands(commands)
            logger.info("Bot commands menu set successfully")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")

    async def error_handler(self, update, context):
        """Handle errors gracefully."""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again."
            )

    def run_bot(self):
        """Run the bot with webhook or polling based on configuration."""
        # Check if bot token is valid
        if self.config.BOT_TOKEN == "placeholder_token":
            logger.error(
                "Bot cannot start without valid BOT_TOKEN. Please set your bot token."
            )
            print("\n🚨 SETUP REQUIRED:")
            print("1. Get your bot token from @BotFather on Telegram")
            print("2. Set BOT_TOKEN environment variable")
            print(
                "3. Set OWNER_ID environment variable (your Telegram user ID)")
            print("\nExample:")
            print("export BOT_TOKEN='your_token_here'")
            print("export OWNER_ID='your_user_id'")
            return

        try:
            application = Application.builder().token(
                self.config.BOT_TOKEN).build()

            # Add handlers
            application.add_handler(
                CommandHandler("start", self.bot_handlers.start_command))
            application.add_handler(
                CommandHandler("help", self.bot_handlers.help_command))
            application.add_handler(
                CommandHandler("settings", self.bot_handlers.settings_command))
            application.add_handler(
                CommandHandler("stats", self.bot_handlers.stats_command))
            application.add_handler(
                CommandHandler("format", self.bot_handlers.format_command))
            application.add_handler(
                CommandHandler("getfmt", self.bot_handlers.getfmt_command))
            application.add_handler(
                CommandHandler("clear", self.bot_handlers.clear_command))
            application.add_handler(
                CommandHandler("set_media", self.bot_handlers.set_media_command))
            application.add_handler(
                CommandHandler("metadata", self.bot_handlers.metadata_command))
            application.add_handler(
                CommandHandler("mode", self.bot_handlers.mode_command))
            application.add_handler(
                CommandHandler("broadcast",
                               self.admin_handlers.broadcast_command))
            application.add_handler(
                CommandHandler("ban", self.admin_handlers.ban_command))
            application.add_handler(
                CommandHandler("unban", self.admin_handlers.unban_command))
            application.add_handler(
                CommandHandler("admin", self.admin_handlers.admin_command))
            application.add_handler(
                CommandHandler("dump", self.admin_handlers.dump_command))

            # Callback query handler for inline keyboards
            application.add_handler(
                CallbackQueryHandler(self.bot_handlers.button_callback))

            # Message handlers
            application.add_handler(
                MessageHandler(filters.Document.ALL | filters.VIDEO,
                               self.bot_handlers.handle_file))
            application.add_handler(
                MessageHandler(filters.PHOTO,
                               self.bot_handlers.handle_thumbnail))
            application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               self.bot_handlers.handle_text))

            # Error handler
            application.add_error_handler(self.error_handler)

            if self.config.USE_WEBHOOK:
                # Webhook mode for production
                logger.info(
                    f"Starting bot with webhook on port {self.config.PORT}")
                application.run_webhook(
                    listen="0.0.0.0",
                    port=self.config.PORT,
                    url_path="/webhook",
                    webhook_url=f"{self.config.WEBHOOK_URL}/webhook")
            else:
                # Polling mode for development
                logger.info("Starting bot with polling...")
                application.run_polling(allowed_updates=None)

        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise


def main():
    """Main entry point."""
    logger.info("Starting Telegram Auto-Rename Bot...")

    try:
        bot = AutoRenameBot()
        bot.run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
