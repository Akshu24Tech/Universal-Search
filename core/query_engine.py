"""
Universal Search — RAG Query Engine
Retrieves relevant chunks and generates grounded, cited answers via Gemini.
"""

import logging
from typing import List, Dict, Any, Optional, Generator

import google.generativeai as genai

from core.embedder import EmbeddingEngine
from core.vector_store import VectorStoreBase

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Universal Search, an AI research assistant built for academic research.
Answer the user's question using ONLY the provided context from their uploaded files.

RULES:
- Cite your sources using [Source: filename, page/timestamp] format
- If the answer spans multiple sources, synthesize and cite each
- If you cannot find the answer in the context, say so clearly — do NOT fabricate information
- Be specific, detailed, and academically rigorous in your answers
- Use markdown formatting for structure (headers, bullets, bold) where helpful
- When quoting directly from a source, use blockquotes

CONTEXT:
{context}

USER QUESTION: {question}"""


class QueryEngine:
    """RAG pipeline: embed query → retrieve → build prompt → generate."""

    def __init__(
        self,
        embedder: EmbeddingEngine,
        vector_store: VectorStoreBase,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.3,
        top_k: int = 5,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.model_name = model_name
        self.temperature = temperature
        self.top_k = top_k
        self.model = genai.GenerativeModel(
            model_name,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
            ),
        )

    def query(self, question: str, stream: bool = True):
        """
        Execute the full RAG pipeline.
        Returns a streaming generator if stream=True, else a string.
        """
        # Step 1: Embed the query
        logger.info(f"Embedding query: {question[:80]}...")
        query_embedding = self.embedder.embed_query(question)

        # Step 2: Retrieve relevant chunks
        logger.info(f"Retrieving top-{self.top_k} chunks...")
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=self.top_k,
        )

        if not results["documents"]:
            no_context_msg = (
                "I couldn't find any relevant information in your uploaded files "
                "to answer this question. Please upload relevant documents first."
            )
            if stream:
                def _empty_stream():
                    yield no_context_msg
                return _empty_stream(), []
            return no_context_msg, []

        # Step 3: Build grounded prompt with citations
        context_parts = []
        sources = []
        for i, (doc, meta, dist) in enumerate(
            zip(results["documents"], results["metadatas"], results["distances"])
        ):
            source_info = self._format_source(meta)
            # Cosine distance → similarity score
            similarity = round((1.0 - dist) * 100, 1)
            context_parts.append(
                f"[Chunk {i + 1}] (Source: {source_info}, Relevance: {similarity}%)\n{doc}"
            )
            sources.append(
                {
                    "chunk_index": i + 1,
                    "source": source_info,
                    "content": doc,
                    "similarity": similarity,
                    "metadata": meta,
                }
            )

        context = "\n\n---\n\n".join(context_parts)
        prompt = SYSTEM_PROMPT.format(context=context, question=question)

        # Step 4: Generate answer
        logger.info(f"Generating answer with {self.model_name}...")
        if stream:
            response = self.model.generate_content(prompt, stream=True)
            return self._stream_response(response), sources
        else:
            response = self.model.generate_content(prompt)
            return response.text, sources

    def _stream_response(self, response) -> Generator[str, None, None]:
        """Yield text chunks from a streaming response."""
        try:
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\n⚠️ Streaming interrupted: {e}"

    @staticmethod
    def _format_source(metadata: Dict[str, Any]) -> str:
        """Format source info from chunk metadata."""
        source = metadata.get("source", "Unknown")
        source_type = metadata.get("type", "unknown")

        if source_type == "pdf":
            page = metadata.get("page", "?")
            return f"{source}, Page {page}"
        elif source_type == "audio":
            time_start = metadata.get("time_start", "?")
            time_end = metadata.get("time_end", "?")
            return f"{source}, {time_start}–{time_end}"
        elif source_type == "video":
            timestamp = metadata.get("timestamp", "?")
            return f"{source}, {timestamp}"
        else:
            return source

    def generate_suggested_questions(
        self, num_questions: int = 4
    ) -> List[str]:
        """Generate starter questions based on indexed content."""
        stats = self.vector_store.get_stats()
        if stats.get("total_chunks", 0) == 0:
            return []

        # Sample a few chunks to understand the content
        # Use a neutral query to get diverse chunks
        try:
            sample_embedding = self.embedder.embed_query(
                "What is the main topic discussed in these documents?"
            )
            results = self.vector_store.query(
                query_embedding=sample_embedding, n_results=5
            )
            if not results["documents"]:
                return []

            sample_text = "\n".join(results["documents"][:5])
            prompt = f"""Based on the following content from uploaded academic documents, 
suggest exactly {num_questions} interesting and specific questions a researcher might ask. 
Return ONLY the questions, one per line, no numbering.

CONTENT SAMPLE:
{sample_text[:2000]}"""

            response = self.model.generate_content(prompt)
            questions = [
                q.strip() for q in response.text.strip().split("\n") if q.strip()
            ]
            return questions[:num_questions]
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []
