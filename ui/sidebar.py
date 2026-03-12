"""
Universal Search — Sidebar Component
The Control Center: file upload, settings, stats, and actions.
"""

import streamlit as st
from ui.theme import THEME

# Accepted file types
ACCEPTED_FILE_TYPES = [
    "pdf",
    "mp3", "wav", "ogg", "m4a", "flac",
    "mp4", "avi", "mov", "mkv", "webm",
]

FILE_TYPE_ICONS = {
    "pdf": "📄",
    "mp3": "🎵", "wav": "🎵", "ogg": "🎵", "m4a": "🎵", "flac": "🎵",
    "mp4": "🎬", "avi": "🎬", "mov": "🎬", "mkv": "🎬", "webm": "🎬",
}

MODALITY_MAP = {
    "pdf": "document",
    "mp3": "audio", "wav": "audio", "ogg": "audio", "m4a": "audio", "flac": "audio",
    "mp4": "video", "avi": "video", "mov": "video", "mkv": "video", "webm": "video",
}


def render_sidebar():
    """Render the full sidebar control center."""
    with st.sidebar:
        # ── Logo & Title ──
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
                <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">🔍</div>
                <h2 style="margin: 0; font-size: 1.4rem; 
                    background: {THEME['gradient']}; 
                    -webkit-background-clip: text; 
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-weight: 800;">Universal Search</h2>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; 
                    color: {THEME['text_muted']}; letter-spacing: 0.1em;
                    text-transform: uppercase;">Multimodal RAG Engine</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── API Key ──
        api_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            placeholder="Enter your Gemini API key...",
            help="Get your API key from https://aistudio.google.com/apikey",
        )
        if api_key:
            st.session_state.api_key = api_key
            st.markdown(
                f'<span style="color: {THEME["success"]}; font-size: 0.8rem;">✓ API key set</span>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        # ── File Uploader ──
        uploaded_files = st.file_uploader(
            "📁 Upload Files",
            type=ACCEPTED_FILE_TYPES,
            accept_multiple_files=True,
            help="Upload PDFs, audio, or video files to search across",
        )
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            _render_file_list(uploaded_files)

        st.markdown("")

        # ── Vector DB Selector ──
        st.markdown(
            f'<p style="font-size: 0.85rem; font-weight: 600; color: {THEME["text"]}; margin-bottom: 0.3rem;">💾 Vector Database</p>',
            unsafe_allow_html=True,
        )
        vector_db = st.radio(
            "Vector Database",
            options=["ChromaDB", "FAISS"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            help="ChromaDB: persistent storage | FAISS: in-memory speed",
        )
        st.session_state.vector_db = vector_db.lower().replace("chromadb", "chromadb").replace("faiss", "faiss")

        st.markdown("")

        # ── Settings ──
        with st.expander("⚙️ Settings", expanded=False):
            st.session_state.chunk_size = st.slider(
                "Chunk Size (tokens)",
                min_value=200,
                max_value=2000,
                value=st.session_state.get("chunk_size", 500),
                step=50,
                help="Size of text chunks for embedding",
            )
            st.session_state.chunk_overlap = st.slider(
                "Chunk Overlap (tokens)",
                min_value=0,
                max_value=200,
                value=st.session_state.get("chunk_overlap", 50),
                step=10,
                help="Overlap between consecutive chunks",
            )
            st.session_state.top_k = st.slider(
                "Top-K Results",
                min_value=1,
                max_value=20,
                value=st.session_state.get("top_k", 5),
                help="Number of chunks to retrieve per query",
            )
            st.session_state.temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get("temperature", 0.3),
                step=0.1,
                help="Creativity of responses (lower = more focused)",
            )
            st.session_state.gen_model = st.selectbox(
                "Generation Model",
                options=["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
                index=0,
                help="Model used for generating answers",
            )

        st.markdown("")

        # ── Action Buttons ──
        col1, col2 = st.columns(2)
        with col1:
            process_clicked = st.button(
                "🚀 Process All",
                use_container_width=True,
                disabled=not (
                    st.session_state.get("api_key")
                    and st.session_state.get("uploaded_files")
                ),
            )
        with col2:
            clear_clicked = st.button(
                "🗑️ Clear KB",
                use_container_width=True,
            )

        if process_clicked:
            st.session_state.should_process = True
        if clear_clicked:
            st.session_state.should_clear = True

        st.markdown("")

        # ── Session Stats ──
        _render_stats()

    return {
        "api_key": st.session_state.get("api_key", ""),
        "uploaded_files": st.session_state.get("uploaded_files", []),
        "vector_db": st.session_state.get("vector_db", "chromadb"),
        "chunk_size": st.session_state.get("chunk_size", 500),
        "chunk_overlap": st.session_state.get("chunk_overlap", 50),
        "top_k": st.session_state.get("top_k", 5),
        "temperature": st.session_state.get("temperature", 0.3),
        "gen_model": st.session_state.get("gen_model", "gemini-2.0-flash"),
        "should_process": st.session_state.get("should_process", False),
        "should_clear": st.session_state.get("should_clear", False),
    }


def _render_file_list(files):
    """Render the uploaded files list with type icons and status badges."""
    processed_files = st.session_state.get("processed_files", set())

    for f in files:
        ext = f.name.split(".")[-1].lower()
        icon = FILE_TYPE_ICONS.get(ext, "📎")
        size = _format_size(f.size)
        is_processed = f.name in processed_files
        status_badge = (
            f'<span style="color: {THEME["success"]}; font-size: 0.75rem;">● indexed</span>'
            if is_processed
            else f'<span style="color: {THEME["text_muted"]}; font-size: 0.75rem;">○ pending</span>'
        )

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between;
                 padding: 0.4rem 0.6rem; margin: 0.2rem 0;
                 background: rgba(19, 19, 26, 0.5); border-radius: 8px;
                 border: 1px solid {THEME['border']};">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>{icon}</span>
                    <span style="font-size: 0.82rem; color: {THEME['text']};">{f.name}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 0.7rem; color: {THEME['text_dim']}; 
                        font-family: 'JetBrains Mono', monospace;">{size}</span>
                    {status_badge}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_stats():
    """Render session statistics."""
    stats = st.session_state.get("index_stats", {})
    total_chunks = stats.get("total_chunks", 0)
    files_processed = len(st.session_state.get("processed_files", set()))
    backend = st.session_state.get("vector_db", "chromadb").upper()

    st.markdown(
        f"""
        <div style="background: {THEME['gradient_subtle']}; border: 1px solid {THEME['border']};
             border-radius: 12px; padding: 0.8rem; margin-top: 0.5rem;">
            <p style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
               color: {THEME['text_muted']}; margin: 0 0 0.5rem 0; font-weight: 600;">Session Stats</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                <div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; 
                        font-weight: 700; color: {THEME['accent']};">{total_chunks}</span>
                    <span style="font-size: 0.7rem; color: {THEME['text_muted']}; display: block;">Chunks</span>
                </div>
                <div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem;
                        font-weight: 700; color: {THEME['accent2']};">{files_processed}</span>
                    <span style="font-size: 0.7rem; color: {THEME['text_muted']}; display: block;">Files</span>
                </div>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.7rem; color: {THEME['text_dim']};
               font-family: 'JetBrains Mono', monospace;">Backend: {backend}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"
