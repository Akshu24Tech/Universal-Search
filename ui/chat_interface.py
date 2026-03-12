"""
Universal Search — Chat Interface
Chat UI with streaming responses and citation cards.
"""

import streamlit as st
from ui.theme import THEME


def render_chat_interface():
    """
    Render the chat interface with message history, citations, and input.
    Uses st.chat_message for proper Streamlit chat display.
    """
    # ── Initialize chat history ──
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ── Chat Header ──
    _render_chat_header()

    # ── Suggested Questions ──
    suggestions = st.session_state.get("suggested_questions", [])
    if suggestions and not st.session_state.messages:
        _render_suggestions(suggestions)

    # ── Message History ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🔍" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                _render_citations(msg["sources"])

    # ── Chat Input ──
    user_input = st.chat_input(
        "Ask anything about your uploaded files...",
        disabled=not st.session_state.get("ready_to_query", False),
    )

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant", avatar="🔍"):
            _handle_query(user_input)

    return user_input


def _render_chat_header():
    """Render the chat area header."""
    stats = st.session_state.get("index_stats", {})
    total_chunks = stats.get("total_chunks", 0)
    files_count = len(st.session_state.get("processed_files", set()))

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; 
             padding: 0.5rem 0 1rem 0; border-bottom: 1px solid {THEME['border']}; margin-bottom: 1rem;">
            <div>
                <h2 style="margin: 0; font-size: 1.3rem !important;
                    background: {THEME['gradient']}; -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent; background-clip: text;">
                    💬 Research Chat
                </h2>
                <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: {THEME['text_muted']};">
                    Ask questions about your uploaded research materials
                </p>
            </div>
            <div style="text-align: right;">
                <span class="accent-badge">{total_chunks} chunks indexed</span>
                <span style="display: block; font-size: 0.7rem; color: {THEME['text_dim']}; 
                    margin-top: 0.3rem;">{files_count} file{'s' if files_count != 1 else ''} loaded</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_suggestions(suggestions: list):
    """Render suggested starter questions."""
    st.markdown(
        f"""
        <p style="font-size: 0.8rem; color: {THEME['text_muted']}; margin-bottom: 0.5rem;
           text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">
            ✨ Suggested Questions
        </p>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(min(len(suggestions), 2))
    for i, q in enumerate(suggestions[:4]):
        with cols[i % 2]:
            if st.button(
                f"💡 {q}",
                key=f"suggestion_{i}",
                use_container_width=True,
            ):
                st.session_state.pending_question = q
                st.rerun()

    # Handle pending question from suggestion click
    if st.session_state.get("pending_question"):
        pending = st.session_state.pop("pending_question")
        st.session_state.messages.append({"role": "user", "content": pending})
        st.rerun()


def _handle_query(question: str):
    """Execute RAG query and display streaming response."""
    query_engine = st.session_state.get("query_engine")
    if not query_engine:
        st.error("Query engine not initialized. Please process files first.")
        return

    try:
        with st.spinner(""):
            response_stream, sources = query_engine.query(question, stream=True)

        # Stream the response
        full_response = st.write_stream(response_stream)

        # Show citations
        if sources:
            _render_citations(sources)

        # Save to history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "sources": sources,
            }
        )

    except Exception as e:
        error_msg = f"⚠️ Error generating response: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append(
            {"role": "assistant", "content": error_msg}
        )


def _render_citations(sources: list):
    """Render source citation cards."""
    if not sources:
        return

    with st.expander(f"📚 Sources ({len(sources)} references)", expanded=False):
        for src in sources:
            similarity = src.get("similarity", 0)
            source_name = src.get("source", "Unknown")
            content_preview = src.get("content", "")[:200]
            metadata = src.get("metadata", {})

            # Similarity color
            if similarity >= 80:
                sim_color = THEME["success"]
            elif similarity >= 60:
                sim_color = THEME["accent"]
            else:
                sim_color = THEME["warning"]

            # Type-specific info
            type_info = ""
            source_type = metadata.get("type", "")
            if source_type == "pdf":
                page = metadata.get("page", "?")
                type_info = f'<span style="font-size: 0.7rem; color: {THEME["text_dim"]};">📄 Page {page}</span>'
            elif source_type == "audio":
                ts = metadata.get("time_start", "?")
                te = metadata.get("time_end", "?")
                type_info = f'<span style="font-size: 0.7rem; color: {THEME["text_dim"]};">🎵 {ts}–{te}</span>'
            elif source_type == "video":
                ts = metadata.get("timestamp", "?")
                type_info = f'<span style="font-size: 0.7rem; color: {THEME["text_dim"]};">🎬 {ts}</span>'

            st.markdown(
                f"""
                <div class="source-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; font-size: 0.85rem; color: {THEME['text']};">{source_name}</span>
                        <div style="display: flex; align-items: center; gap: 0.6rem;">
                            {type_info}
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; 
                                color: {sim_color}; font-weight: 600;">{similarity}%</span>
                        </div>
                    </div>
                    <p style="color: {THEME['text_muted']}; font-size: 0.8rem; margin: 0; line-height: 1.5;
                       font-style: italic;">{content_preview}{'...' if len(src.get('content', '')) > 200 else ''}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
