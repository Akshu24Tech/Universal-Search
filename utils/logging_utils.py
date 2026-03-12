"""
Universal Search — Logging Utilities
Processing log manager with timestamps, errors, and performance metrics.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingLog:
    """Manages a log of processing steps with timestamps and metrics."""

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self._timers: Dict[str, float] = {}

    def log(self, message: str, level: str = "info", file: str = None):
        """Add a log entry."""
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
            "file": file,
        }
        self.entries.append(entry)
        getattr(logger, level, logger.info)(
            f"[{entry['timestamp']}] {message}"
        )

    def info(self, message: str, file: str = None):
        self.log(message, "info", file)

    def warning(self, message: str, file: str = None):
        self.log(message, "warning", file)

    def error(self, message: str, file: str = None):
        self.log(message, "error", file)

    def start_timer(self, name: str):
        """Start a named timer."""
        self._timers[name] = time.time()
        self.info(f"Started: {name}")

    def stop_timer(self, name: str) -> float:
        """Stop a named timer and return elapsed time in seconds."""
        if name not in self._timers:
            return 0.0
        elapsed = time.time() - self._timers.pop(name)
        self.info(f"Completed: {name} ({elapsed:.2f}s)")
        return elapsed

    def get_formatted_entries(self, last_n: int = None) -> List[str]:
        """Get formatted log entries for display."""
        entries = self.entries[-last_n:] if last_n else self.entries
        formatted = []
        for e in entries:
            level_icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(
                e["level"], "•"
            )
            file_tag = f" [{e['file']}]" if e.get("file") else ""
            formatted.append(
                f"{e['timestamp']} {level_icon}{file_tag} {e['message']}"
            )
        return formatted

    def get_metrics(self) -> Dict[str, Any]:
        """Get summary metrics from the log."""
        total = len(self.entries)
        errors = sum(1 for e in self.entries if e["level"] == "error")
        warnings = sum(1 for e in self.entries if e["level"] == "warning")
        return {
            "total_entries": total,
            "errors": errors,
            "warnings": warnings,
            "info": total - errors - warnings,
        }

    def clear(self):
        """Clear all log entries."""
        self.entries.clear()
        self._timers.clear()
