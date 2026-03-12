"""
Universal Search — Knowledge Base Explorer
Chunk browser, distribution charts, and embedding visualization.
"""

import streamlit as st
import numpy as np
from ui.theme import THEME


def render_knowledge_explorer():
    """Render the Knowledge Base Explorer panel."""
    chunks_data = st.session_state.get("chunks_data", [])
    if not chunks_data:
        st.info("No chunks indexed yet. Upload and process files first.")
        return

    st.markdown(
        f"""
        <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid {THEME['border']}; margin-bottom: 1rem;">
            <h2 style="margin: 0; font-size: 1.3rem !important;
                background: {THEME['gradient']}; -webkit-background-clip: text;
                -webkit-text-fill-color: transparent; background-clip: text;">
                🧠 Knowledge Base Explorer
            </h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: {THEME['text_muted']};">
                Inspect indexed chunks, view distribution, and explore embeddings
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📋 Chunks", "📊 Distribution", "🗺️ Embeddings"])

    with tab1:
        _render_chunks_table(chunks_data)

    with tab2:
        _render_distribution(chunks_data)

    with tab3:
        _render_embedding_viz()


def _render_chunks_table(chunks_data: list):
    """Render searchable chunks table."""
    import pandas as pd

    # Search filter
    search = st.text_input("🔍 Filter chunks...", placeholder="Type to filter by content or source")

    # Build table data
    rows = []
    for i, chunk in enumerate(chunks_data):
        meta = chunk.get("metadata", {})
        content = chunk.get("content", "")
        rows.append(
            {
                "ID": i + 1,
                "Source": meta.get("source", "Unknown"),
                "Type": meta.get("type", "?").upper(),
                "Preview": content[:100] + "..." if len(content) > 100 else content,
                "Tokens": chunk.get("token_count", len(content) // 4),
                "Page/Time": meta.get("page", meta.get("timestamp", meta.get("time_start", "—"))),
            }
        )

    df = pd.DataFrame(rows)

    # Apply search filter
    if search:
        mask = df.apply(
            lambda row: search.lower() in str(row).lower(), axis=1
        )
        df = df[mask]

    st.markdown(
        f'<p style="color: {THEME["text_muted"]}; font-size: 0.8rem;">'
        f"Showing {len(df)} of {len(rows)} chunks</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(df, use_container_width=True, height=400)

    # Chunk detail viewer
    if len(chunks_data) > 0:
        with st.expander("📖 View Full Chunk"):
            chunk_idx = st.number_input(
                "Chunk ID", min_value=1, max_value=len(chunks_data), value=1
            )
            selected = chunks_data[chunk_idx - 1]
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display: flex; gap: 0.8rem; margin-bottom: 0.8rem;">
                        <span class="accent-badge">{selected.get('metadata', {}).get('source', 'Unknown')}</span>
                        <span class="accent-badge">{selected.get('metadata', {}).get('type', '?').upper()}</span>
                    </div>
                    <p style="color: {THEME['text']}; font-size: 0.9rem; line-height: 1.7; white-space: pre-wrap;">
                        {selected.get('content', 'No content')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_distribution(chunks_data: list):
    """Render chunk distribution charts."""
    import plotly.graph_objects as go

    if not chunks_data:
        return

    # ── By Source File ──
    source_counts = {}
    type_counts = {"pdf": 0, "audio": 0, "video": 0}

    for chunk in chunks_data:
        meta = chunk.get("metadata", {})
        source = meta.get("source", "Unknown")
        ctype = meta.get("type", "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
        if ctype in type_counts:
            type_counts[ctype] += 1

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<p style="color: {THEME["text"]}; font-weight: 600; font-size: 0.9rem;">Chunks by Source</p>',
            unsafe_allow_html=True,
        )
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(source_counts.keys()),
                    values=list(source_counts.values()),
                    hole=0.55,
                    marker=dict(
                        colors=_generate_colors(len(source_counts)),
                        line=dict(color=THEME["bg"], width=2),
                    ),
                    textinfo="label+percent",
                    textfont=dict(color=THEME["text"], size=11),
                )
            ]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=THEME["text_muted"]),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            f'<p style="color: {THEME["text"]}; font-weight: 600; font-size: 0.9rem;">Chunks by Modality</p>',
            unsafe_allow_html=True,
        )
        modality_colors = {
            "pdf": THEME["accent"],
            "audio": THEME["accent2"],
            "video": THEME["warning"],
        }
        active_types = {k: v for k, v in type_counts.items() if v > 0}
        fig2 = go.Figure(
            data=[
                go.Bar(
                    x=list(active_types.keys()),
                    y=list(active_types.values()),
                    marker_color=[
                        modality_colors.get(t, THEME["text_muted"])
                        for t in active_types.keys()
                    ],
                    text=list(active_types.values()),
                    textposition="outside",
                    textfont=dict(color=THEME["text"]),
                )
            ]
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=THEME["text_muted"]),
            margin=dict(l=20, r=20, t=20, b=40),
            height=300,
            xaxis=dict(gridcolor=THEME["border"]),
            yaxis=dict(gridcolor=THEME["border"]),
        )
        st.plotly_chart(fig2, use_container_width=True)


def _render_embedding_viz():
    """Render 2D t-SNE embedding visualization."""
    embeddings = st.session_state.get("embeddings_list", [])
    chunks_data = st.session_state.get("chunks_data", [])

    if not embeddings or len(embeddings) < 3:
        st.info("Need at least 3 embedded chunks for visualization. Upload and process more files.")
        return

    try:
        from sklearn.manifold import TSNE
        import plotly.graph_objects as go

        # Run t-SNE
        with st.spinner("Computing t-SNE embedding visualization..."):
            emb_array = np.array(embeddings)
            perplexity = min(30, len(embeddings) - 1)
            tsne = TSNE(n_components=2, random_state=42, perplexity=max(1, perplexity))
            coords = tsne.fit_transform(emb_array)

        # Color by source file
        sources = [c.get("metadata", {}).get("source", "Unknown") for c in chunks_data]
        unique_sources = list(set(sources))
        colors = _generate_colors(len(unique_sources))
        color_map = {s: c for s, c in zip(unique_sources, colors)}
        point_colors = [color_map[s] for s in sources]

        fig = go.Figure()
        for source in unique_sources:
            mask = [i for i, s in enumerate(sources) if s == source]
            fig.add_trace(
                go.Scatter(
                    x=coords[mask, 0],
                    y=coords[mask, 1],
                    mode="markers",
                    name=source,
                    marker=dict(size=8, opacity=0.8),
                    text=[
                        chunks_data[i].get("content", "")[:80] + "..."
                        for i in mask
                    ],
                    hovertemplate="%{text}<extra>%{fullData.name}</extra>",
                )
            )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=THEME["text_muted"]),
            margin=dict(l=20, r=20, t=30, b=20),
            height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(
                bgcolor="rgba(19,19,26,0.8)",
                bordercolor=THEME["border"],
                borderwidth=1,
                font=dict(size=11),
            ),
            title=dict(
                text="Embedding Space (t-SNE)",
                font=dict(color=THEME["text"], size=14),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.warning("Install scikit-learn for embedding visualization: `pip install scikit-learn`")
    except Exception as e:
        st.error(f"Visualization error: {e}")


def _generate_colors(n: int) -> list:
    """Generate a harmonious color palette."""
    base_colors = [
        "#8B5CF6",  # violet
        "#06B6D4",  # cyan
        "#F59E0B",  # amber
        "#22C55E",  # green
        "#EF4444",  # red
        "#EC4899",  # pink
        "#3B82F6",  # blue
        "#F97316",  # orange
    ]
    if n <= len(base_colors):
        return base_colors[:n]
    # Cycle through colors if more are needed
    return [base_colors[i % len(base_colors)] for i in range(n)]
