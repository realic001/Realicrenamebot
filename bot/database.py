"""
Database module for managing bot data including users, admins, formats, and dump channels.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class Database:
    """Database handler for bot data management."""
    
    def __init__(self, db_path: str = "bot_data.db"):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables."""
        with self.lock:
            conn = self.get_connection()
            try:
                # Users table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        is_banned BOOLEAN DEFAULT FALSE,
                        is_admin BOOLEAN DEFAULT FALSE,
                        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        files_renamed INTEGER DEFAULT 0,
                        total_size INTEGER DEFAULT 0
                    )
                ''')
                
                # User settings table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id INTEGER PRIMARY KEY,
                        rename_mode TEXT DEFAULT 'auto',
                        media_type TEXT DEFAULT 'document',
                        custom_format TEXT DEFAULT '{title}',
                        auto_thumbnail BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Format templates table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS format_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT,
                        template TEXT,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Dump channels table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS dump_channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel_id INTEGER,
                        channel_name TEXT,
                        added_by INTEGER,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (added_by) REFERENCES users (user_id)
                    )
                ''')
                
                # File processing history
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS file_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        original_name TEXT,
                        new_name TEXT,
                        file_size INTEGER,
                        file_type TEXT,
                        processing_time REAL,
                        processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Rate limiting table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS rate_limits (
                        user_id INTEGER PRIMARY KEY,
                        request_count INTEGER DEFAULT 0,
                        window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
            except Exception as e:
                logger.error(f"Database initialization error: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Add or update user in database."""
        with self.lock:
            conn = self.get_connection()
            try:
                # Check if user exists
                existing = conn.execute(
                    "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
                ).fetchone()
                
                if existing:
                    # Update existing user
                    conn.execute('''
                        UPDATE users 
                        SET username = ?, first_name = ?, last_name = ?, last_activity = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (username, first_name, last_name, user_id))
                else:
                    # Add new user
                    conn.execute('''
                        INSERT INTO users (user_id, username, first_name, last_name)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, username, first_name, last_name))
                    
                    # Add default settings
                    conn.execute('''
                        INSERT INTO user_settings (user_id)
                        VALUES (?)
                    ''', (user_id,))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Error adding user {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information."""
        conn = self.get_connection()
        try:
            result = conn.execute('''
                SELECT u.*, s.rename_mode, s.media_type, s.custom_format, s.auto_thumbnail
                FROM users u
                LEFT JOIN user_settings s ON u.user_id = s.user_id
                WHERE u.user_id = ?
            ''', (user_id,)).fetchone()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
        finally:
            conn.close()
    
    def is_banned(self, user_id: int) -> bool:
        """Check if user is banned."""
        conn = self.get_connection()
        try:
            result = conn.execute(
                "SELECT is_banned FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return bool(result['is_banned']) if result else False
        except Exception as e:
            logger.error(f"Error checking ban status for {user_id}: {e}")
            return False
        finally:
            conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        conn = self.get_connection()
        try:
            result = conn.execute(
                "SELECT is_admin FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return bool(result['is_admin']) if result else False
        except Exception as e:
            logger.error(f"Error checking admin status for {user_id}: {e}")
            return False
        finally:
            conn.close()
    
    def ban_user(self, user_id: int) -> bool:
        """Ban a user."""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute(
                    "UPDATE users SET is_banned = TRUE WHERE user_id = ?", (user_id,)
                )
                conn.commit()
                return conn.rowcount > 0
            except Exception as e:
                logger.error(f"Error banning user {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def unban_user(self, user_id: int) -> bool:
        """Unban a user."""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute(
                    "UPDATE users SET is_banned = FALSE WHERE user_id = ?", (user_id,)
                )
                conn.commit()
                return conn.rowcount > 0
            except Exception as e:
                logger.error(f"Error unbanning user {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def set_admin(self, user_id: int, is_admin: bool = True) -> bool:
        """Set user admin status."""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute(
                    "UPDATE users SET is_admin = ? WHERE user_id = ?", (is_admin, user_id)
                )
                conn.commit()
                return conn.rowcount > 0
            except Exception as e:
                logger.error(f"Error setting admin status for {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def update_user_settings(self, user_id: int, **kwargs) -> bool:
        """Update user settings."""
        if not kwargs:
            return False
            
        with self.lock:
            conn = self.get_connection()
            try:
                # Build dynamic update query
                set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
                values = list(kwargs.values()) + [user_id]
                
                conn.execute(f'''
                    UPDATE user_settings 
                    SET {set_clause}
                    WHERE user_id = ?
                ''', values)
                
                conn.commit()
                return conn.rowcount > 0
            except Exception as e:
                logger.error(f"Error updating settings for {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def add_file_history(self, user_id: int, original_name: str, new_name: str, 
                        file_size: int, file_type: str, processing_time: float) -> bool:
        """Add file processing history."""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute('''
                    INSERT INTO file_history 
                    (user_id, original_name, new_name, file_size, file_type, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, original_name, new_name, file_size, file_type, processing_time))
                
                # Update user statistics
                conn.execute('''
                    UPDATE users 
                    SET files_renamed = files_renamed + 1, 
                        total_size = total_size + ?,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (file_size, user_id))
                
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding file history: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        conn = self.get_connection()
        try:
            # Get basic stats
            user_stats = conn.execute('''
                SELECT files_renamed, total_size, join_date, last_activity
                FROM users WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if not user_stats:
                return {}
            
            # Get recent activity
            recent_files = conn.execute('''
                SELECT COUNT(*) as count
                FROM file_history 
                WHERE user_id = ? AND processed_date > datetime('now', '-7 days')
            ''', (user_id,)).fetchone()
            
            return {
                'files_renamed': user_stats['files_renamed'],
                'total_size': user_stats['total_size'],
                'join_date': user_stats['join_date'],
                'last_activity': user_stats['last_activity'],
                'recent_files': recent_files['count'] if recent_files else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {user_id}: {e}")
            return {}
        finally:
            conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get user leaderboard."""
        conn = self.get_connection()
        try:
            results = conn.execute('''
                SELECT user_id, username, first_name, files_renamed, total_size
                FROM users 
                WHERE is_banned = FALSE
                ORDER BY files_renamed DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
        finally:
            conn.close()
    
    def add_dump_channel(self, channel_id: int, channel_name: str, added_by: int) -> bool:
        """Add dump channel."""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO dump_channels 
                    (channel_id, channel_name, added_by)
                    VALUES (?, ?, ?)
                ''', (channel_id, channel_name, added_by))
                
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding dump channel: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def remove_dump_channel(self, channel_id: int) -> bool:
        """Remove dump channel."""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute(
                    "DELETE FROM dump_channels WHERE channel_id = ?", (channel_id,)
                )
                conn.commit()
                return conn.rowcount > 0
            except Exception as e:
                logger.error(f"Error removing dump channel: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def get_dump_channels(self) -> List[Dict]:
        """Get all active dump channels."""
        conn = self.get_connection()
        try:
            results = conn.execute('''
                SELECT channel_id, channel_name, added_date
                FROM dump_channels 
                WHERE is_active = TRUE
                ORDER BY added_date DESC
            ''').fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting dump channels: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs for broadcasting."""
        conn = self.get_connection()
        try:
            results = conn.execute(
                "SELECT user_id FROM users WHERE is_banned = FALSE"
            ).fetchall()
            
            return [row['user_id'] for row in results]
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
        finally:
            conn.close()
    
    def check_rate_limit(self, user_id: int, max_requests: int = 5, window_seconds: int = 60) -> bool:
        """Check if user is within rate limits."""
        with self.lock:
            conn = self.get_connection()
            try:
                now = datetime.now()
                window_start = now - timedelta(seconds=window_seconds)
                
                # Get current rate limit data
                result = conn.execute(
                    "SELECT request_count, window_start FROM rate_limits WHERE user_id = ?",
                    (user_id,)
                ).fetchone()
                
                if not result:
                    # First request
                    conn.execute('''
                        INSERT INTO rate_limits (user_id, request_count, window_start)
                        VALUES (?, 1, ?)
                    ''', (user_id, now))
                    conn.commit()
                    return True
                
                # Check if window has expired
                if datetime.fromisoformat(result['window_start']) < window_start:
                    # Reset window
                    conn.execute('''
                        UPDATE rate_limits 
                        SET request_count = 1, window_start = ?
                        WHERE user_id = ?
                    ''', (now, user_id))
                    conn.commit()
                    return True
                
                # Check rate limit
                if result['request_count'] >= max_requests:
                    return False
                
                # Increment counter
                conn.execute('''
                    UPDATE rate_limits 
                    SET request_count = request_count + 1
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Error checking rate limit for {user_id}: {e}")
                return True  # Allow on error
            finally:
                conn.close()
