"""
Complete bot/file_manager.py file content for GitHub upload
Copy this entire content to your bot/file_manager.py file
"""

import os
import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable
import aiofiles
import ffmpeg
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON
from mutagen.mp4 import MP4
from PIL import Image

from .database import Database
from .utils import FileUtils, TextUtils, TimeUtils
from config import Config

logger = logging.getLogger(__name__)

class FileManager:
    """Handles all file processing operations."""
    
    def __init__(self, database: Database):
        """Initialize file manager with database and config."""
        self.db = database
        self.config = Config()
        
    async def process_file(self, file_obj, file_type: str, user_data: Dict,
                          progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Process file with automatic naming."""
        start_time = time.time()
        
        try:
            # Download file
            if progress_callback:
                await progress_callback("📥 Downloading file...")
            
            file_path = await self.download_file(file_obj, progress_callback)
            if not file_path:
                return {'success': False, 'error': 'Failed to download file'}
            
            # Get file info
            if progress_callback:
                await progress_callback("📋 Extracting file information...")
            
            file_info = await self.get_file_info_detailed(file_path)
            
            # Generate new filename
            if progress_callback:
                await progress_callback("🔄 Generating filename...")
            
            custom_format = user_data.get('custom_format', '{title}')
            new_filename = await self.generate_filename(file_info, custom_format)
            
            # Rename file
            if progress_callback:
                await progress_callback("✏️ Renaming file...")
            
            renamed_path = await self.rename_file(file_path, new_filename)
            if not renamed_path:
                return {'success': False, 'error': 'Failed to rename file'}
            
            # Process metadata if enabled
            if user_data.get('auto_thumbnail', True):
                if progress_callback:
                    await progress_callback("🖼️ Processing metadata...")
                await self.process_metadata(renamed_path, file_info, user_data)
            
            # Record in database
            processing_time = time.time() - start_time
            user_id = user_data.get('user_id')
            if user_id:
                self.db.add_file_history(
                    user_id,
                    file_obj.file_name or "unknown",
                    new_filename,
                    file_obj.file_size or 0,
                    file_type,
                    processing_time
                )
            
            return {
                'success': True,
                'file_path': renamed_path,
                'filename': new_filename,
                'file_type': file_type,
                'original_name': file_obj.file_name,
                'file_size': file_obj.file_size,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_file_with_name(self, file_obj, file_type: str, custom_name: str,
                                   user_data: Dict, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Process file with custom filename."""
        start_time = time.time()
        
        try:
            # Download file
            if progress_callback:
                await progress_callback("📥 Downloading file...")
            
            file_path = await self.download_file(file_obj, progress_callback)
            if not file_path:
                return {'success': False, 'error': 'Failed to download file'}
            
            # Sanitize custom name
            safe_filename = TextUtils.sanitize_filename(custom_name)
            
            # Add extension if missing
            original_ext = FileUtils.get_file_extension(file_obj.file_name or "")
            if not safe_filename.lower().endswith(original_ext.lower()):
                safe_filename += original_ext
            
            # Rename file
            if progress_callback:
                await progress_callback("✏️ Applying custom name...")
            
            renamed_path = await self.rename_file(file_path, safe_filename)
            if not renamed_path:
                return {'success': False, 'error': 'Failed to rename file'}
            
            # Get file info for metadata
            file_info = await self.get_file_info_detailed(renamed_path)
            
            # Process metadata if enabled
            if user_data.get('auto_thumbnail', True):
                if progress_callback:
                    await progress_callback("🖼️ Processing metadata...")
                await self.process_metadata(renamed_path, file_info, user_data)
            
            # Record in database
            processing_time = time.time() - start_time
            user_id = user_data.get('user_id')
            if user_id:
                self.db.add_file_history(
                    user_id,
                    file_obj.file_name or "unknown",
                    safe_filename,
                    file_obj.file_size or 0,
                    file_type,
                    processing_time
                )
            
            return {
                'success': True,
                'file_path': renamed_path,
                'filename': safe_filename,
                'file_type': file_type,
                'original_name': file_obj.file_name,
                'file_size': file_obj.file_size,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing file with custom name: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_file(self, file_obj, progress_callback: Optional[Callable] = None) -> Optional[str]:
        """Download file from Telegram servers."""
        try:
            # Get file from Telegram
            file = await file_obj.get_file()
            
            # Generate unique filename
            timestamp = str(int(time.time()))
            original_name = file_obj.file_name or f"file_{timestamp}"
            safe_name = TextUtils.sanitize_filename(original_name)
            
            file_path = os.path.join(self.config.DOWNLOAD_PATH, f"{timestamp}_{safe_name}")
            
            # Download with progress tracking
            if file_obj.file_size and file_obj.file_size > 10 * 1024 * 1024:  # 10MB+
                # For large files, show progress
                downloaded_size = 0
                total_size = file_obj.file_size
                
                async def download_progress():
                    nonlocal downloaded_size
                    while downloaded_size < total_size:
                        if os.path.exists(file_path):
                            downloaded_size = os.path.getsize(file_path)
                            if progress_callback:
                                progress = (downloaded_size / total_size) * 100
                                await progress_callback(f"📥 Downloading... {progress:.1f}%")
                        await asyncio.sleep(1)
                
                # Start progress tracking
                progress_task = asyncio.create_task(download_progress())
                
                # Download file
                await file.download_to_drive(file_path)
                
                # Stop progress tracking
                progress_task.cancel()
            else:
                # For smaller files, download directly
                await file.download_to_drive(file_path)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    async def rename_file(self, file_path: str, new_name: str) -> Optional[str]:
        """Rename file to new filename."""
        try:
            directory = os.path.dirname(file_path)
            new_path = os.path.join(directory, new_name)
            
            # Ensure unique filename
            counter = 1
            base_name, ext = os.path.splitext(new_name)
            while os.path.exists(new_path):
                new_name = f"{base_name}_{counter}{ext}"
                new_path = os.path.join(directory, new_name)
                counter += 1
            
            os.rename(file_path, new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            return None
    
    async def process_metadata(self, file_path: str, file_info: Dict, user_data: Dict) -> bool:
        """Process file metadata and thumbnails."""
        try:
            file_ext = FileUtils.get_file_extension(file_path).lower()
            
            if file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
                return await self.process_video_metadata(file_path, file_info, user_data)
            elif file_ext in ['.mp3', '.flac', '.aac', '.ogg', '.wav', '.m4a']:
                return await self.process_audio_metadata(file_path, file_info, user_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing metadata: {e}")
            return False
    
    async def process_video_metadata(self, file_path: str, file_info: Dict, user_data: Dict) -> bool:
        """Process video file metadata and thumbnails."""
        try:
            # Extract thumbnail if requested
            if user_data.get('auto_thumbnail', True):
                thumbnail_path = await self.extract_video_thumbnail(file_path)
                if thumbnail_path:
                    # Optional: Add thumbnail to video metadata
                    pass
            
            # Add metadata using ffmpeg
            metadata = {
                'title': file_info.get('title', ''),
                'artist': file_info.get('artist', ''),
                'album': file_info.get('album', ''),
                'date': file_info.get('year', ''),
                'genre': file_info.get('genre', ''),
                'comment': f"Processed by Auto-Rename Bot"
            }
            
            # Create output path
            temp_path = file_path + ".temp"
            
            # Apply metadata
            try:
                (
                    ffmpeg
                    .input(file_path)
                    .output(temp_path, **{f'metadata:{k}': v for k, v in metadata.items() if v})
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                # Replace original file
                os.replace(temp_path, file_path)
                
            except ffmpeg.Error as e:
                logger.warning(f"FFmpeg metadata error: {e}")
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing video metadata: {e}")
            return False
    
    async def process_audio_metadata(self, file_path: str, file_info: Dict, user_data: Dict) -> bool:
        """Process audio file metadata."""
        try:
            audio_file = MutagenFile(file_path)
            if not audio_file:
                return False
            
            # Set common metadata
            metadata_map = {
                'title': ['TIT2', '\xa9nam', 'TITLE'],
                'artist': ['TPE1', '\xa9ART', 'ARTIST'],
                'album': ['TALB', '\xa9alb', 'ALBUM'],
                'year': ['TDRC', '\xa9day', 'DATE'],
                'genre': ['TCON', '\xa9gen', 'GENRE']
            }
            
            for field, keys in metadata_map.items():
                value = file_info.get(field, '')
                if value:
                    for key in keys:
                        try:
                            if hasattr(audio_file, 'tags') and audio_file.tags is not None:
                                if key.startswith('T'):  # ID3 tags
                                    audio_file.tags[key] = getattr(globals().get(key, str), 'text', [value])
                                elif key.startswith('\xa9'):  # MP4 tags
                                    audio_file.tags[key] = [value]
                                else:  # Other formats
                                    audio_file.tags[key] = value
                        except:
                            continue
            
            # Save changes
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error processing audio metadata: {e}")
            return False
    
    async def extract_video_thumbnail(self, video_path: str) -> Optional[str]:
        """Extract thumbnail from video file."""
        try:
            # Generate thumbnail filename
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            thumbnail_path = os.path.join(self.config.TEMP_PATH, f"{base_name}_thumb.jpg")
            
            # Extract thumbnail using ffmpeg
            (
                ffmpeg
                .input(video_path, ss=30)  # Extract at 30 seconds
                .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return thumbnail_path if os.path.exists(thumbnail_path) else None
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {e}")
            return None
    
    async def get_file_info_detailed(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information."""
        try:
            file_stats = os.stat(file_path)
            base_info = {
                'filename': os.path.basename(file_path),
                'size': file_stats.st_size,
                'modified': TimeUtils.format_timestamp(file_stats.st_mtime),
                'extension': FileUtils.get_file_extension(file_path),
                'type': 'unknown'
            }
            
            # Get file type specific info
            type_info = await self.get_file_type_info(file_path)
            base_info.update(type_info)
            
            # Extract metadata if possible
            try:
                audio_file = MutagenFile(file_path)
                if audio_file and audio_file.tags:
                    # Extract common metadata
                    metadata = {
                        'title': self._extract_tag(audio_file, ['TIT2', '\xa9nam', 'TITLE']),
                        'artist': self._extract_tag(audio_file, ['TPE1', '\xa9ART', 'ARTIST']),
                        'album': self._extract_tag(audio_file, ['TALB', '\xa9alb', 'ALBUM']),
                        'year': self._extract_tag(audio_file, ['TDRC', '\xa9day', 'DATE']),
                        'genre': self._extract_tag(audio_file, ['TCON', '\xa9gen', 'GENRE']),
                        'duration': getattr(audio_file, 'info', {}).length if hasattr(audio_file, 'info') else 0
                    }
                    base_info.update({k: v for k, v in metadata.items() if v})
            except:
                pass  # Metadata extraction failed, continue with basic info
            
            # Fallback title from filename
            if 'title' not in base_info or not base_info['title']:
                base_info['title'] = os.path.splitext(base_info['filename'])[0]
            
            return base_info
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {'title': 'Unknown File', 'filename': os.path.basename(file_path)}
    
    def _extract_tag(self, audio_file, tag_keys: list) -> str:
        """Extract tag value from audio file."""
        if not audio_file.tags:
            return ""
        
        for key in tag_keys:
            try:
                value = audio_file.tags.get(key)
                if value:
                    if isinstance(value, list):
                        return str(value[0]) if value else ""
                    return str(value)
            except:
                continue
        return ""
    
    async def cleanup_temp_files(self, user_id: int) -> None:
        """Clean up temporary files for user."""
        try:
            # Clean files older than 1 hour
            current_time = time.time()
            
            for directory in [self.config.DOWNLOAD_PATH, self.config.TEMP_PATH]:
                if not os.path.exists(directory):
                    continue
                
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > 3600:  # 1 hour
                            try:
                                os.remove(file_path)
                            except:
                                pass
                                
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
    
    async def validate_file(self, file_obj) -> tuple[bool, str]:
        """Validate file before processing."""
        try:
            # Check file size
            if file_obj.file_size and file_obj.file_size > self.config.MAX_FILE_SIZE:
                return False, f"File too large. Maximum size: {FileUtils.format_file_size(self.config.MAX_FILE_SIZE)}"
            
            # Check file extension
            filename = file_obj.file_name or ""
            ext = FileUtils.get_file_extension(filename).lower()
            
            supported_exts = {
                '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                '.mp3', '.flac', '.aac', '.ogg', '.wav', '.m4a',
                '.pdf', '.doc', '.docx', '.txt', '.zip', '.rar', '.7z'
            }
            
            if ext not in supported_exts:
                return False, f"Unsupported file type: {ext}"
            
            return True, "Valid file"
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return False, "Validation error"
    
    async def get_file_type_info(self, file_path: str) -> Dict[str, str]:
        """Get file type specific information."""
        try:
            ext = FileUtils.get_file_extension(file_path).lower()
            
            if ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
                return await self._get_video_info(file_path)
            elif ext in ['.mp3', '.flac', '.aac', '.ogg', '.wav', '.m4a']:
                return await self._get_audio_info(file_path)
            else:
                return {'type': 'document'}
                
        except Exception as e:
            logger.error(f"Error getting file type info: {e}")
            return {'type': 'unknown'}
    
    async def _get_video_info(self, file_path: str) -> Dict[str, str]:
        """Get video file information."""
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if video_stream:
                return {
                    'type': 'video',
                    'codec': video_stream.get('codec_name', 'unknown'),
                    'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                    'duration': float(video_stream.get('duration', 0))
                }
            
            return {'type': 'video'}
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {'type': 'video'}
    
    async def _get_audio_info(self, file_path: str) -> Dict[str, str]:
        """Get audio file information."""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file and hasattr(audio_file, 'info'):
                return {
                    'type': 'audio',
                    'bitrate': getattr(audio_file.info, 'bitrate', 0),
                    'duration': getattr(audio_file.info, 'length', 0),
                    'channels': getattr(audio_file.info, 'channels', 0)
                }
            
            return {'type': 'audio'}
            
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {'type': 'audio'}
    
    async def generate_filename(self, file_info: Dict, format_template: str) -> str:
        """Generate filename from template and file info."""
        try:
            # Available variables for template
            variables = {
                'title': file_info.get('title', 'Untitled'),
                'artist': file_info.get('artist', 'Unknown Artist'),
                'author': file_info.get('artist', 'Unknown Author'),
                'album': file_info.get('album', 'Unknown Album'),
                'genre': file_info.get('genre', 'Unknown Genre'),
                'year': file_info.get('year', 'Unknown Year'),
                'audio': f"{file_info.get('bitrate', 0)}kbps" if file_info.get('type') == 'audio' else '',
                'video': file_info.get('resolution', '') if file_info.get('type') == 'video' else '',
                'codec': file_info.get('codec', ''),
                'resolution': file_info.get('resolution', ''),
                'duration': TimeUtils.format_duration(file_info.get('duration', 0)),
                'size': FileUtils.format_file_size(file_info.get('size', 0))
            }
            
            # Replace template variables
            filename = format_template
            for var, value in variables.items():
                filename = filename.replace(f'{{{var}}}', str(value))
            
            # Sanitize filename
            filename = TextUtils.sanitize_filename(filename)
            
            # Add original extension
            original_ext = file_info.get('extension', '')
            if not filename.lower().endswith(original_ext.lower()):
                filename += original_ext
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            return f"renamed_file{file_info.get('extension', '')}"
