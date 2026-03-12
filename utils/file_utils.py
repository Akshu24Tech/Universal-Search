"""
Universal Search — File Utilities
File type detection, temp directory management, and size formatting.
"""

import os
import tempfile
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# File type mappings
MODALITY_MAP = {
    ".pdf": "document",
    ".mp3": "audio",
    ".wav": "audio",
    ".ogg": "audio",
    ".m4a": "audio",
    ".flac": "audio",
    ".aac": "audio",
    ".wma": "audio",
    ".mp4": "video",
    ".avi": "video",
    ".mov": "video",
    ".mkv": "video",
    ".webm": "video",
}

MIME_MAP = {
    ".pdf": "application/pdf",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
    ".flac": "audio/flac",
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
}


def get_file_modality(filename: str) -> str:
    """Get the modality of a file (document, audio, video)."""
    ext = os.path.splitext(filename)[1].lower()
    return MODALITY_MAP.get(ext, "unknown")


def get_file_mime_type(filename: str) -> str:
    """Get the MIME type for a file."""
    ext = os.path.splitext(filename)[1].lower()
    return MIME_MAP.get(ext, "application/octet-stream")


def get_file_icon(filename: str) -> str:
    """Get an emoji icon for a file type."""
    modality = get_file_modality(filename)
    icons = {"document": "📄", "audio": "🎵", "video": "🎬"}
    return icons.get(modality, "📎")


def format_file_size(size_bytes: int) -> str:
    """Format byte count into human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def save_temp_file(file_bytes: bytes, filename: str) -> str:
    """Save bytes to a temporary file and return the path."""
    ext = os.path.splitext(filename)[1] or ".tmp"
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(file_bytes)
    tmp.close()
    logger.debug(f"Saved temp file: {tmp.name}")
    return tmp.name


def cleanup_temp_file(path: str):
    """Remove a temporary file if it exists."""
    try:
        if path and os.path.exists(path):
            os.unlink(path)
            logger.debug(f"Cleaned up temp file: {path}")
    except Exception as e:
        logger.warning(f"Failed to clean up {path}: {e}")


def ensure_data_dir(path: str = "data") -> str:
    """Ensure the data directory exists."""
    os.makedirs(path, exist_ok=True)
    return path
