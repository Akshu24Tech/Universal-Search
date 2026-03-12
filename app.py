"""
Universal Search — Main Application
Multimodal RAG Engine for Academic Research
Powered by Gemini Interleaved Embeddings

Run: streamlit run app.py
"""

import os
import uuid
import logging
import streamlit as st
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ──────────────────────────────────────────────
# Page Config (MUST be first Streamlit call)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Universal Search — Multimodal RAG",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Imports (after page config)
# ──────────────────────────────────────────────
from ui.theme import inject_theme
from ui.sidebar import render_sidebar
from ui.hero_section import render_hero
from ui.processing_dashboard import render_processing_dashboard, create_initial_processing_state
from ui.chat_interface import render_chat_interface
from ui.knowledge_explorer import render_knowledge_explorer

from core.embedder import EmbeddingEngine
from core.chunker import TextChunker
from core.vector_store import create_vector_store
from core.query_engine import QueryEngine

from processors.pdf_processor import PDFProcessor
from processors.audio_processor import AudioProcessor
from processors.video_processor import VideoProcessor

from utils.file_utils import get_file_modality, save_temp_file, cleanup_temp_file
from utils.logging_utils import ProcessingLog


# ──────────────────────────────────────────────
# Theme Injection
# ──────────────────────────────────────────────
inject_theme()


# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "uploaded_files": [],
        "processed_files": set(),
        "vector_db": "chromadb",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "top_k": 5,
        "temperature": 0.3,
        "gen_model": "gemini-2.0-flash",
        "should_process": False,
        "should_clear": False,
        "is_processing": False,
        "ready_to_query": False,
        "messages": [],
        "chunks_data": [],
        "embeddings_list": [],
        "index_stats": {},
        "processing_log": ProcessingLog(),
        "processing_state": None,
        "query_engine": None,
        "vector_store": None,
        "suggested_questions": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
sidebar_config = render_sidebar()


# ──────────────────────────────────────────────
# Handle "Clear Knowledge Base"
# ──────────────────────────────────────────────
if st.session_state.get("should_clear"):
    st.session_state.should_clear = False
    st.session_state.processed_files = set()
    st.session_state.chunks_data = []
    st.session_state.embeddings_list = []
    st.session_state.index_stats = {}
    st.session_state.messages = []
    st.session_state.ready_to_query = False
    st.session_state.query_engine = None
    st.session_state.suggested_questions = []
    st.session_state.processing_log = ProcessingLog()
    if st.session_state.get("vector_store"):
        try:
            st.session_state.vector_store.clear()
        except Exception:
            pass
    st.session_state.vector_store = None
    st.toast("🗑️ Knowledge base cleared!", icon="✓")
    st.rerun()


# ──────────────────────────────────────────────
# Handle "Process All Files"
# ──────────────────────────────────────────────
if st.session_state.get("should_process"):
    st.session_state.should_process = False

    files = st.session_state.get("uploaded_files", [])
    api_key = st.session_state.get("api_key", "")

    if not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar.")
    elif not files:
        st.warning("📁 No files to process. Upload files in the sidebar.")
    else:
        st.session_state.is_processing = True
        st.rerun()


# ──────────────────────────────────────────────
# FILE PROCESSING PIPELINE
# ──────────────────────────────────────────────
def run_processing_pipeline(files, api_key: str):
    """Execute the full multimodal ingestion pipeline."""
    plog = st.session_state.processing_log
    plog.clear()
    plog.start_timer("total_pipeline")

    # Initialize components
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    embedder = EmbeddingEngine(api_key)
    chunker = TextChunker(
        chunk_size=st.session_state.chunk_size,
        chunk_overlap=st.session_state.chunk_overlap,
    )

    # Create vector store
    db_backend = st.session_state.vector_db
    if db_backend == "chromadb":
        vector_store = create_vector_store("chromadb", persist_dir="data/chroma_db")
    else:
        vector_store = create_vector_store("faiss")
    st.session_state.vector_store = vector_store

    # Processors
    pdf_proc = PDFProcessor()
    audio_proc = AudioProcessor()
    video_proc = VideoProcessor()

    all_chunks = []
    all_embeddings = []
    processing_state = create_initial_processing_state(files)

    progress_container = st.container()
    overall_bar = st.progress(0.0)
    status_text = st.empty()

    total_files = len(files)

    for file_idx, uploaded_file in enumerate(files):
        filename = uploaded_file.name
        modality = get_file_modality(filename)
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset for potential re-read

        plog.info(f"Processing: {filename} ({modality})", filename)
        processing_state["files"][filename]["status"] = "processing"

        try:
            # ── Step 1: EXTRACT ──
            processing_state["files"][filename]["current_step"] = 0
            processing_state["files"][filename]["message"] = "Extracting content..."
            processing_state["files"][filename]["progress"] = 0.1
            status_text.markdown(f"📥 **Extracting:** `{filename}`")
            plog.start_timer(f"extract_{filename}")

            if modality == "document":
                result = pdf_proc.process(file_bytes=file_bytes, filename=filename)
                raw_chunks = pdf_proc.get_page_chunks(result)
            elif modality == "audio":
                result = audio_proc.process(file_bytes=file_bytes, filename=filename)
                raw_chunks = audio_proc.get_segment_chunks(result)
            elif modality == "video":
                tmp_path = save_temp_file(file_bytes, filename)
                try:
                    result = video_proc.process(file_path=tmp_path, filename=filename)
                    raw_chunks = video_proc.get_video_chunks(result)
                finally:
                    cleanup_temp_file(tmp_path)
            else:
                plog.warning(f"Unsupported file type: {filename}", filename)
                processing_state["files"][filename]["status"] = "error"
                processing_state["files"][filename]["message"] = "Unsupported format"
                continue

            plog.stop_timer(f"extract_{filename}")

            # ── Step 2: CHUNK ──
            processing_state["files"][filename]["current_step"] = 1
            processing_state["files"][filename]["message"] = f"Chunking ({len(raw_chunks)} segments)..."
            processing_state["files"][filename]["progress"] = 0.35
            status_text.markdown(f"✂️ **Chunking:** `{filename}` ({len(raw_chunks)} segments)")
            plog.start_timer(f"chunk_{filename}")

            file_chunks = []
            for raw_chunk in raw_chunks:
                text_chunks = chunker.chunk_text(
                    raw_chunk["content"],
                    metadata=raw_chunk["metadata"],
                )
                # Attach images to first chunk from this raw segment
                for i, tc in enumerate(text_chunks):
                    tc["images"] = raw_chunk.get("images", []) if i == 0 else []
                file_chunks.extend(text_chunks)

            plog.stop_timer(f"chunk_{filename}")
            plog.info(f"Created {len(file_chunks)} chunks from {filename}", filename)

            # ── Step 3: EMBED ──
            processing_state["files"][filename]["current_step"] = 2
            processing_state["files"][filename]["message"] = f"Embedding {len(file_chunks)} chunks..."
            processing_state["files"][filename]["progress"] = 0.6
            status_text.markdown(f"🧬 **Embedding:** `{filename}` ({len(file_chunks)} chunks)")
            plog.start_timer(f"embed_{filename}")

            chunk_embeddings = []
            for chunk in file_chunks:
                images = chunk.get("images", [])
                if images and len(images) > 0:
                    # Interleaved embedding (text + first image)
                    try:
                        emb = embedder.embed_interleaved(
                            chunk["content"], images[0]
                        )
                    except Exception:
                        # Fallback to text-only
                        emb = embedder.embed_text(chunk["content"])
                else:
                    emb = embedder.embed_text(chunk["content"])
                chunk_embeddings.append(emb)

            plog.stop_timer(f"embed_{filename}")

            # ── Step 4: INDEX ──
            processing_state["files"][filename]["current_step"] = 3
            processing_state["files"][filename]["message"] = "Indexing in vector database..."
            processing_state["files"][filename]["progress"] = 0.85
            status_text.markdown(f"📦 **Indexing:** `{filename}`")
            plog.start_timer(f"index_{filename}")

            chunk_ids = [str(uuid.uuid4()) for _ in file_chunks]
            chunk_texts = [c["content"] for c in file_chunks]
            chunk_metas = [c["metadata"] for c in file_chunks]

            vector_store.add_documents(
                embeddings=chunk_embeddings,
                documents=chunk_texts,
                metadatas=chunk_metas,
                ids=chunk_ids,
            )

            plog.stop_timer(f"index_{filename}")

            # ── Done ──
            processing_state["files"][filename]["status"] = "done"
            processing_state["files"][filename]["current_step"] = 4
            processing_state["files"][filename]["progress"] = 1.0
            processing_state["files"][filename]["message"] = f"✓ {len(file_chunks)} chunks indexed"

            all_chunks.extend(file_chunks)
            all_embeddings.extend(chunk_embeddings)
            st.session_state.processed_files.add(filename)

        except Exception as e:
            plog.error(f"Failed: {filename} — {str(e)}", filename)
            processing_state["files"][filename]["status"] = "error"
            processing_state["files"][filename]["message"] = f"Error: {str(e)[:100]}"

        # Update overall progress
        overall = (file_idx + 1) / total_files
        processing_state["overall_progress"] = overall
        overall_bar.progress(overall)

    # ── Pipeline Complete ──
    total_time = plog.stop_timer("total_pipeline")

    # Save state
    st.session_state.chunks_data = all_chunks
    st.session_state.embeddings_list = all_embeddings
    st.session_state.index_stats = vector_store.get_stats()
    st.session_state.is_processing = False

    # Initialize query engine
    query_engine = QueryEngine(
        embedder=embedder,
        vector_store=vector_store,
        model_name=st.session_state.gen_model,
        temperature=st.session_state.temperature,
        top_k=st.session_state.top_k,
    )
    st.session_state.query_engine = query_engine
    st.session_state.ready_to_query = True

    # Generate suggested questions
    status_text.markdown("✨ **Generating suggested questions...**")
    try:
        suggestions = query_engine.generate_suggested_questions()
        st.session_state.suggested_questions = suggestions
    except Exception:
        st.session_state.suggested_questions = []

    status_text.empty()
    overall_bar.empty()

    plog.info(f"Pipeline complete! {len(all_chunks)} total chunks in {total_time:.1f}s")
    st.toast(
        f"✅ Processed {len(st.session_state.processed_files)} files — "
        f"{len(all_chunks)} chunks indexed in {total_time:.1f}s",
        icon="🎉",
    )
    st.rerun()


# ──────────────────────────────────────────────
# MAIN CONTENT ROUTING
# ──────────────────────────────────────────────
if st.session_state.get("is_processing"):
    # Show processing dashboard
    run_processing_pipeline(
        st.session_state.uploaded_files,
        st.session_state.api_key,
    )

elif st.session_state.get("ready_to_query"):
    # Chat + Knowledge Explorer
    tab1, tab2 = st.tabs(["💬 Research Chat", "🧠 Knowledge Explorer"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_knowledge_explorer()

else:
    # Hero section (empty state)
    render_hero()
