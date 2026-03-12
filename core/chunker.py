"""
Universal Search — Recursive Text Splitter
Chunks text into overlapping segments while preserving metadata.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TextChunker:
    """Recursive text splitter with configurable chunk size and overlap."""

    # Split hierarchy: paragraphs → sentences → words
    SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks with metadata.

        Returns list of dicts: {
            "content": str,
            "metadata": {source, type, chunk_index, ...},
            "token_count": int
        }
        """
        if not text or not text.strip():
            return []

        base_metadata = metadata or {}
        raw_chunks = self._recursive_split(text, self.SEPARATORS)

        # Merge small chunks and apply overlap
        merged = self._merge_with_overlap(raw_chunks)

        results = []
        for i, chunk_text in enumerate(merged):
            chunk_meta = {**base_metadata, "chunk_index": i}
            results.append(
                {
                    "content": chunk_text.strip(),
                    "metadata": chunk_meta,
                    "token_count": self._estimate_tokens(chunk_text),
                }
            )

        logger.info(
            f"Chunked text into {len(results)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        return results

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separator hierarchy."""
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        parts = text.split(separator)

        chunks = []
        for part in parts:
            if self._estimate_tokens(part) <= self.chunk_size:
                if part.strip():
                    chunks.append(part)
            else:
                # Recursively split with next separator
                sub_chunks = self._recursive_split(part, remaining_separators)
                chunks.extend(sub_chunks)

        return chunks

    def _merge_with_overlap(self, chunks: List[str]) -> List[str]:
        """Merge small chunks and create overlapping windows."""
        if not chunks:
            return []

        merged = []
        current = ""

        for chunk in chunks:
            candidate = (current + " " + chunk).strip() if current else chunk

            if self._estimate_tokens(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    merged.append(current)
                current = chunk

        if current:
            merged.append(current)

        # Apply overlap
        if self.chunk_overlap > 0 and len(merged) > 1:
            overlapped = []
            for i, chunk in enumerate(merged):
                if i > 0:
                    # Get tail of previous chunk as overlap prefix
                    prev_words = merged[i - 1].split()
                    overlap_words = prev_words[-self.chunk_overlap :]
                    overlap_text = " ".join(overlap_words)
                    chunk = overlap_text + " " + chunk
                overlapped.append(chunk)
            return overlapped
        return merged

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 chars per token for English."""
        return len(text) // 4 if text else 0
