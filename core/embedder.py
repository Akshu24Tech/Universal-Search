"""
Universal Search — Gemini Embedding Engine
Supports text-only and interleaved (text + image) embeddings
using gemini-embedding-2-preview.
"""

import time
import logging
from typing import List, Optional, Union

import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "models/gemini-embedding-2-preview"
MAX_BATCH_SIZE = 100
RATE_LIMIT_DELAY = 0.1  # seconds between API calls


class EmbeddingEngine:
    """Wraps Gemini embedding API with batching and interleaved support."""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = EMBEDDING_MODEL
        self._request_count = 0

    def embed_text(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[float]:
        """Embed a single text string."""
        self._rate_limit()
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Text embedding failed: {e}")
            raise

    def embed_interleaved(
        self,
        text: str,
        image: Image.Image,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[float]:
        """Embed interleaved text + image into a single vector."""
        self._rate_limit()
        try:
            result = genai.embed_content(
                model=self.model,
                content=[text, image],
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Interleaved embedding failed: {e}")
            raise

    def embed_batch(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> List[List[float]]:
        """Embed a batch of text strings."""
        all_embeddings = []
        for i in range(0, len(texts), MAX_BATCH_SIZE):
            batch = texts[i : i + MAX_BATCH_SIZE]
            self._rate_limit()
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=batch,
                    task_type=task_type,
                )
                # API returns list for batch input
                embeddings = result["embedding"]
                if isinstance(embeddings[0], float):
                    # Single item batch returns flat list
                    all_embeddings.append(embeddings)
                else:
                    all_embeddings.extend(embeddings)
            except Exception as e:
                logger.error(f"Batch embedding failed at index {i}: {e}")
                raise
        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """Embed a user query for retrieval."""
        return self.embed_text(query, task_type="RETRIEVAL_QUERY")

    def _rate_limit(self):
        """Simple rate limiting between API calls."""
        self._request_count += 1
        if self._request_count > 1:
            time.sleep(RATE_LIMIT_DELAY)
