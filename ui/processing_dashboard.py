"""
Universal Search — Processing Dashboard
Displays per-file progress with step indicators and animated bars.
"""

import streamlit as st
from ui.theme import THEME


PROCESSING_STEPS = [
    ("📥", "Extracting", "Pulling text & media from file"),
    ("✂️", "Chunking", "Splitting into searchable segments"),
    ("🧬", "Embedding", "Creating vector representations"),
    ("📦", "Indexing", "Adding to vector database"),
]


def render_processing_dashboard(processing_state: dict):
    """
    Render the processing dashboard.

    processing_state: {
        "files": {
            filename: {
                "status": "processing" | "done" | "error",
                "current_step": 0-3,
                "progress": 0.0-1.0,
                "message": str,
                "type": "pdf" | "audio" | "video"
            }
        },
        "overall_progress": 0.0-1.0,
        "log_messages": [str]
    }
    """
    files = processing_state.get("files", {})
    overall = processing_state.get("overall_progress", 0.0)

    # ── Header ──
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
            <h2 style="font-size: 1.6rem !important; margin: 0;
                background: {THEME['gradient']}; -webkit-background-clip: text;
                -webkit-text-fill-color: transparent; background-clip: text;">
                ⚡ Processing Files
            </h2>
            <p style="color: {THEME['text_muted']}; font-size: 0.85rem; margin-top: 0.3rem;">
                Ingesting your files into the knowledge base...
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Overall Progress ──
    st.progress(overall)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # ── Per-file Progress Cards ──
    for filename, file_state in files.items():
        _render_file_card(filename, file_state)

    # ── Live Log ──
    log_messages = processing_state.get("log_messages", [])
    if log_messages:
        with st.expander("📋 Processing Log", expanded=False):
            for msg in log_messages[-20:]:  # Show last 20
                st.markdown(
                    f'<p style="font-family: \'JetBrains Mono\', monospace; font-size: 0.75rem; '
                    f'color: {THEME["text_muted"]}; margin: 0.15rem 0; line-height: 1.4;">{msg}</p>',
                    unsafe_allow_html=True,
                )


def _render_file_card(filename: str, state: dict):
    """Render a single file's processing card."""
    status = state.get("status", "pending")
    current_step = state.get("current_step", 0)
    progress = state.get("progress", 0.0)
    message = state.get("message", "")
    file_type = state.get("type", "document")

    type_icons = {"pdf": "📄", "audio": "🎵", "video": "🎬", "document": "📄"}
    icon = type_icons.get(file_type, "📎")

    status_colors = {
        "processing": THEME["accent"],
        "done": THEME["success"],
        "error": THEME["error"],
        "pending": THEME["text_muted"],
    }
    status_color = status_colors.get(status, THEME["text_muted"])

    # Build step indicators
    steps_html = ""
    for i, (step_icon, step_name, step_desc) in enumerate(PROCESSING_STEPS):
        if i < current_step:
            step_class = "done"
            indicator = "✓"
            color = THEME["success"]
        elif i == current_step and status == "processing":
            step_class = "active"
            indicator = step_icon
            color = THEME["accent"]
        else:
            step_class = ""
            indicator = step_icon
            color = THEME["text_dim"]

        steps_html += f"""
            <div class="processing-step {step_class}" style="color: {color};">
                <span>{indicator}</span>
                <span style="font-size: 0.8rem;">{step_name}</span>
            </div>
        """

    st.markdown(
        f"""
        <div class="glass-card" style="margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.3rem;">{icon}</span>
                    <div>
                        <span style="color: {THEME['text']}; font-weight: 600; font-size: 0.9rem;">{filename}</span>
                        <br/>
                        <span style="color: {THEME['text_muted']}; font-size: 0.75rem;">
                            {message if message else 'Waiting...'}
                        </span>
                    </div>
                </div>
                <span style="color: {status_color}; font-size: 0.8rem; font-weight: 600;
                    text-transform: uppercase; letter-spacing: 0.05em;">
                    {'● ' + status if status != 'processing' else '<span class="pulse">● processing</span>'}
                </span>
            </div>
            <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                {steps_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if status == "processing":
        st.progress(progress)


def create_initial_processing_state(files) -> dict:
    """Create the initial processing state from uploaded files."""
    from ui.sidebar import MODALITY_MAP

    state = {
        "files": {},
        "overall_progress": 0.0,
        "log_messages": [],
    }

    for f in files:
        ext = f.name.split(".")[-1].lower()
        modality = MODALITY_MAP.get(ext, "document")
        state["files"][f.name] = {
            "status": "pending",
            "current_step": 0,
            "progress": 0.0,
            "message": "Queued for processing",
            "type": modality,
        }

    return state
