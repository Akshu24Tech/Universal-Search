"""
Universal Search — Vector Store Abstraction
Unified interface for ChromaDB (persistent) and FAISS (in-memory).
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

import numpy as np

logger = logging.getLogger(__name__)


class VectorStoreBase(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        pass

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        pass


class ChromaDBStore(VectorStoreBase):
    """ChromaDB persistent vector store."""

    def __init__(self, persist_dir: str = "data/chroma_db", collection_name: str = "universal_search"):
        import chromadb

        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB initialized at {persist_dir}, collection: {collection_name}")

    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        # ChromaDB metadata values must be str, int, float, or bool
        sanitized_metas = []
        for meta in metadatas:
            sanitized = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    sanitized[k] = v
                else:
                    sanitized[k] = str(v)
            sanitized_metas.append(sanitized)

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=sanitized_metas,
            ids=ids,
        )
        logger.info(f"Added {len(ids)} documents to ChromaDB")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        return {
            "ids": results["ids"][0] if results["ids"] else [],
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
        }

    def clear(self) -> None:
        import chromadb

        self.client.delete_collection("universal_search")
        self.collection = self.client.get_or_create_collection(
            name="universal_search",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB collection cleared")

    def get_stats(self) -> Dict[str, Any]:
        count = self.collection.count()
        return {
            "backend": "ChromaDB",
            "total_chunks": count,
            "persist_dir": self.persist_dir,
        }


class FAISSStore(VectorStoreBase):
    """FAISS in-memory vector store."""

    def __init__(self, dimension: int = 3072):
        import faiss

        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []
        logger.info(f"FAISS initialized with dimension {dimension}")

    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        vectors = np.array(embeddings, dtype="float32")
        # L2 normalize for cosine similarity via inner product
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors = vectors / norms

        self.index.add(vectors)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
        logger.info(f"Added {len(ids)} documents to FAISS")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> Dict[str, Any]:
        query_vec = np.array([query_embedding], dtype="float32")
        # Normalize query
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        n_results = min(n_results, self.index.ntotal)
        if n_results == 0:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

        scores, indices = self.index.search(query_vec, n_results)

        result_ids = []
        result_docs = []
        result_metas = []
        result_distances = []

        for i, idx in enumerate(indices[0]):
            if idx < 0:
                continue
            result_ids.append(self.ids[idx])
            result_docs.append(self.documents[idx])
            result_metas.append(self.metadatas[idx])
            # Convert inner product score to distance-like metric (1 - score)
            result_distances.append(float(1.0 - scores[0][i]))

        return {
            "ids": result_ids,
            "documents": result_docs,
            "metadatas": result_metas,
            "distances": result_distances,
        }

    def clear(self) -> None:
        import faiss

        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents.clear()
        self.metadatas.clear()
        self.ids.clear()
        logger.info("FAISS index cleared")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "backend": "FAISS",
            "total_chunks": self.index.ntotal,
            "dimension": self.dimension,
        }


def create_vector_store(
    backend: str = "chromadb",
    **kwargs,
) -> VectorStoreBase:
    """Factory function to create the selected vector store."""
    if backend.lower() == "chromadb":
        return ChromaDBStore(**kwargs)
    elif backend.lower() == "faiss":
        return FAISSStore(**kwargs)
    else:
        raise ValueError(f"Unknown vector store backend: {backend}")
