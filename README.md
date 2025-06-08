# Telegram Auto-Rename Bot

A comprehensive Python-based Telegram bot for intelligent file management with advanced renaming capabilities, thumbnail management, and admin controls.

## Features

### Core Functionality
- **Auto & Manual Rename Modes**: Choose between automatic renaming with templates or manual control
- **Custom Format Templates**: Use metadata variables like `{title}`, `{author}`, `{artist}`, etc.
- **File Support**: Handle documents, videos, and audio files up to 5GB
- **Word Replacement**: Replace specific words in filenames

### Thumbnail Management
- **Extract Thumbnails**: Pull thumbnail images from video files
- **Custom Thumbnails**: Set custom thumbnails for videos
- **Save & Delete**: Manage thumbnail storage
- **Steal Thumbnails**: Copy thumbnails from other files

### Metadata Editing
- **File Information**: View comprehensive file details
- **Set Metadata**: Edit title, author, artist, album, genre, year
- **Audio/Video Info**: Access codec, resolution, duration details

### User Interface
- **Menu-Driven Interface**: Easy-to-use inline keyboard navigation
- **Statistics Tracking**: Personal file processing statistics
- **Leaderboard System**: User activity rankings
- **Rate Limiting**: Protection against abuse

### Admin Features
- **User Management**: Ban/unban users, promote/demote admins
- **Broadcasting**: Send messages to all users
- **Dump Channels**: Auto-forward processed files to designated channels
- **Bot Statistics**: Comprehensive usage analytics

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- FFmpeg (for video/audio processing)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 2. Environment Configuration

Create environment variables for deployment:

```bash
# Required
BOT_TOKEN=your_bot_token_from_botfather
OWNER_ID=your_telegram_user_id

# Optional
USE_WEBHOOK=false
WEBHOOK_URL=https://your-domain.com
PORT=5000
MAX_FILE_SIZE=5368709120
```

### 3. Running the Bot

#### Local Development
```bash
python main.py
```

#### Production Deployment
Set environment variables in your hosting platform:
- `BOT_TOKEN`: Get from @BotFather
- `OWNER_ID`: Your Telegram user ID
- `USE_WEBHOOK=true`: For production
- `WEBHOOK_URL`: Your domain URL
- `PORT=8080`: Or your preferred port

## Commands

### User Commands
- `/start` - Initialize bot and show welcome screen
- `/help` - Display help information
- `/settings` - Configure bot preferences
- `/format` - Manage format templates
- `/stats` - View personal statistics

### Admin Commands
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/admin add <user_id>` - Promote user to admin
- `/admin remove <user_id>` - Remove admin status
- `/broadcast <message>` - Send message to all users
- `/dump add <channel_id>` - Add dump channel
- `/dump remove <channel_id>` - Remove dump channel
- `/dump list` - List all dump channels

## Format Template Variables

Use these variables in your custom format templates:

| Variable | Description |
|----------|-------------|
| `{title}` | File title/name |
| `{author}` | Author name |
| `{artist}` | Artist name |
| `{album}` | Album name |
| `{genre}` | Genre |
| `{year}` | Year |
| `{audio}` | Audio track information |
| `{video}` | Video information |
| `{resolution}` | Video resolution (e.g., 1080p) |
| `{codec}` | Video codec |
| `{duration}` | File duration |
| `{size}` | File size |

### Example Templates
- `{title} - {artist}` → "Song - Artist"
- `[{year}] {title}` → "[2023] Movie"
- `{title} ({resolution})` → "Video (1080p)"

## Project Structure

```
├── bot/
│   ├── __init__.py
│   ├── admin.py          # Admin functionality
│   ├── commands.py       # Command handlers
│   ├── database.py       # SQLite database management
│   ├── file_manager.py   # File processing logic
│   ├── handlers.py       # Main bot handlers
│   ├── keyboards.py      # Inline keyboard layouts
│   └── utils.py          # Utility functions
├── config.py             # Configuration management
├── main.py              # Bot entry point
├── bot_welcome.png      # Welcome image
└── README.md
```

## Database Schema

The bot uses SQLite with the following tables:
- `users` - User information and statistics
- `user_settings` - Individual user preferences
- `format_templates` - Custom format templates
- `dump_channels` - Configured dump channels
- `file_history` - File processing history
- `rate_limits` - Rate limiting data

## Dependencies

- `python-telegram-bot==20.8` - Telegram Bot API
- `aiofiles` - Async file operations
- `mutagen` - Audio metadata handling
- `ffmpeg-python` - Video/audio processing
- `Pillow` - Image processing

## Deployment

### Replit Deployment
1. Set environment variables in Replit Secrets
2. The bot automatically configures for deployment
3. Use webhook mode for production (`USE_WEBHOOK=true`)

### Other Platforms
1. Set required environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Security Features

- Rate limiting to prevent abuse
- User ban/unban system
- Admin-only commands protection
- Input validation and sanitization
- Secure file handling

## Error Handling

- Comprehensive logging system
- Graceful error recovery
- User-friendly error messages
- Automatic cleanup of temporary files

## Support

For issues or questions:
1. Check the help command: `/help`
2. Review this documentation
3. Contact the bot administrator

---

**Note**: This bot requires proper configuration of environment variables to function. Ensure you have a valid Telegram Bot Token and have set your user ID as the owner before deployment.