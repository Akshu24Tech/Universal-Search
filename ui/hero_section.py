"""
Universal Search — Hero Section
Empty state hero with animated gradient border and feature cards.
"""

import streamlit as st
from ui.theme import THEME


def render_hero():
    """Render the hero section when no files have been processed."""

    # ── Animated Hero Card ──
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem 0;">
            <div class="hero-border" style="max-width: 800px; margin: 0 auto;">
                <div class="hero-inner" style="text-align: center;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">
                        🔍📄🎵🎬
                    </div>
                    <h1 style="font-size: 2.4rem !important; margin: 0 0 0.8rem 0; line-height: 1.2;
                        background: {THEME['gradient']}; -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent; background-clip: text;
                        font-weight: 800 !important;">
                        Drop any PDF, Audio, or Video<br/>— then ask anything.
                    </h1>
                    <p style="color: {THEME['text_muted']}; font-size: 1.05rem; max-width: 560px;
                       margin: 0 auto 1.5rem auto; line-height: 1.6;">
                        Universal Search uses multimodal AI to understand and connect 
                        information across all your research files — papers, lectures, 
                        tutorials, and more.
                    </p>
                    <div style="display: inline-block;">
                        <span class="accent-badge" style="font-size: 0.75rem;">
                            Powered by Gemini Interleaved Embeddings
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # ── Feature Cards ──
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; min-height: 200px;">
                <span class="feature-icon">📄</span>
                <h3 style="font-size: 1.1rem !important; margin: 0 0 0.5rem 0;
                    color: {THEME['text']} !important;">Documents</h3>
                <p style="color: {THEME['text_muted']}; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                    Extract text, tables, and images from PDFs — research papers, 
                    notes, slides, and manuals.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; min-height: 200px;">
                <span class="feature-icon">🎵</span>
                <h3 style="font-size: 1.1rem !important; margin: 0 0 0.5rem 0;
                    color: {THEME['text']} !important;">Audio</h3>
                <p style="color: {THEME['text_muted']}; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                    Transcribe and search spoken content from lectures, 
                    podcasts, meetings, and voice memos.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; min-height: 200px;">
                <span class="feature-icon">🎬</span>
                <h3 style="font-size: 1.1rem !important; margin: 0 0 0.5rem 0;
                    color: {THEME['text']} !important;">Video</h3>
                <p style="color: {THEME['text_muted']}; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                    Extract keyframes and narration from tutorials, 
                    presentations, and screen recordings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── How It Works ──
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align: center; max-width: 700px; margin: 0 auto; padding: 1.5rem 0;">
            <p style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.15em;
               color: {THEME['text_muted']}; font-weight: 600; margin-bottom: 1.2rem;">
                How It Works
            </p>
            <div style="display: flex; justify-content: center; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">📤</div>
                    <span style="font-size: 0.8rem; color: {THEME['text_muted']};">Upload</span>
                </div>
                <span style="color: {THEME['text_dim']}; font-size: 1.2rem;">→</span>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">⚙️</div>
                    <span style="font-size: 0.8rem; color: {THEME['text_muted']};">Process</span>
                </div>
                <span style="color: {THEME['text_dim']}; font-size: 1.2rem;">→</span>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🧬</div>
                    <span style="font-size: 0.8rem; color: {THEME['text_muted']};">Embed</span>
                </div>
                <span style="color: {THEME['text_dim']}; font-size: 1.2rem;">→</span>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🔍</div>
                    <span style="font-size: 0.8rem; color: {THEME['text_muted']};">Search</span>
                </div>
                <span style="color: {THEME['text_dim']}; font-size: 1.2rem;">→</span>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">💡</div>
                    <span style="font-size: 0.8rem; color: {THEME['text_muted']};">Answer</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
