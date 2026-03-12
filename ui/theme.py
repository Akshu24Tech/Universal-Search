"""
Universal Search — Neural Dark Theme
CSS injection for Streamlit with glassmorphism, gradients, and premium aesthetics.
"""

import streamlit as st

# Neural Dark Color Tokens
THEME = {
    "bg": "#0A0A0F",
    "surface": "#13131A",
    "surface_hover": "#1A1A25",
    "accent": "#8B5CF6",
    "accent2": "#06B6D4",
    "accent_glow": "rgba(139, 92, 246, 0.4)",
    "text": "#F1F5F9",
    "text_muted": "#64748B",
    "text_dim": "#475569",
    "border": "rgba(139, 92, 246, 0.15)",
    "border_hover": "rgba(139, 92, 246, 0.3)",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "gradient": "linear-gradient(135deg, #8B5CF6, #06B6D4)",
    "gradient_subtle": "linear-gradient(135deg, rgba(139,92,246,0.1), rgba(6,182,212,0.1))",
}


def inject_theme():
    """Inject the Neural Dark theme CSS into Streamlit."""
    st.markdown(
        f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* ═══════════════════════════════════════════
           GLOBAL RESET & BASE
           ═══════════════════════════════════════════ */
        .stApp {{
            background-color: {THEME['bg']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {THEME['text']};
        }}

        /* Hide default Streamlit branding but keep header functional for sidebar toggle */
        #MainMenu, footer {{
            visibility: hidden;
        }}
        header {{
            background-color: transparent !important;
        }}

        /* ═══════════════════════════════════════════
           NOISE OVERLAY — Premium texture
           ═══════════════════════════════════════════ */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
        }}

        /* ═══════════════════════════════════════════
           SIDEBAR — Control Center
           ═══════════════════════════════════════════ */
        [data-testid="stSidebar"] {{
            background-color: {THEME['surface']};
            border-right: 1px solid {THEME['border']};
        }}
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown li {{
            color: {THEME['text']};
        }}

        /* ═══════════════════════════════════════════
           TYPOGRAPHY
           ═══════════════════════════════════════════ */
        h1, h2, h3, h4, h5, h6 {{
            color: {THEME['text']} !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            hyphens: none !important;
            word-break: keep-all !important;
        }}
        h1 {{
            font-size: 2.2rem !important;
            background: {THEME['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        p, li, span {{
            color: {THEME['text']};
        }}

        /* ═══════════════════════════════════════════
           BUTTONS — Gradient with hover lift
           ═══════════════════════════════════════════ */
        .stButton > button {{
            background: {THEME['gradient']};
            color: white !important;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 0.6rem 1.5rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: 0.01em;
            white-space: nowrap !important;
            width: 100%;
            display: block;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px {THEME['accent_glow']};
        }}
        .stButton > button:active {{
            transform: translateY(0px);
        }}

        /* Secondary / outline buttons */
        .stButton > button[kind="secondary"] {{
            background: transparent;
            border: 1px solid {THEME['border']};
            color: {THEME['text']} !important;
        }}
        .stButton > button[kind="secondary"]:hover {{
            border-color: {THEME['accent']};
            background: rgba(139, 92, 246, 0.08);
        }}

        /* ═══════════════════════════════════════════
           INPUTS & CONTROLS
           ═══════════════════════════════════════════ */
        .stTextInput > div > div > input,
        .stTextArea textarea {{
            background-color: {THEME['surface']} !important;
            color: {THEME['text']} !important;
            border: 1px solid {THEME['border']} !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            transition: border-color 0.3s ease;
        }}
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {{
            border-color: {THEME['accent']} !important;
            box-shadow: 0 0 0 2px {THEME['accent_glow']} !important;
        }}

        /* Sliders */
        .stSlider > div > div > div > div {{
            background: {THEME['gradient']} !important;
        }}

        /* Select boxes */
        .stSelectbox > div > div {{
            background-color: {THEME['surface']} !important;
            border: 1px solid {THEME['border']} !important;
            border-radius: 12px !important;
            color: {THEME['text']} !important;
        }}

        /* Radio buttons */
        .stRadio > div {{
            background-color: transparent;
        }}
        .stRadio label {{
            color: {THEME['text']} !important;
        }}

        /* ═══════════════════════════════════════════
           CHAT MESSAGES
           ═══════════════════════════════════════════ */
        [data-testid="stChatMessage"] {{
            background-color: {THEME['surface']} !important;
            border: 1px solid {THEME['border']};
            border-radius: 16px !important;
            padding: 1.2rem !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}

        /* Chat input */
        .stChatInput {{
            border-color: {THEME['border']} !important;
        }}
        .stChatInput > div {{
            background-color: {THEME['surface']} !important;
            border: 1px solid {THEME['border']} !important;
            border-radius: 16px !important;
        }}

        /* ═══════════════════════════════════════════
           EXPANDERS — Glassmorphism cards
           ═══════════════════════════════════════════ */
        [data-testid="stExpander"] {{
            background-color: rgba(19, 19, 26, 0.8) !important;
            border: 1px solid {THEME['border']} !important;
            border-radius: 16px !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        [data-testid="stExpander"] summary {{
            color: {THEME['text']} !important;
        }}

        /* ═══════════════════════════════════════════
           METRICS — Glowing cards
           ═══════════════════════════════════════════ */
        [data-testid="stMetric"] {{
            background-color: {THEME['surface']};
            border: 1px solid {THEME['border']};
            border-radius: 12px;
            padding: 1rem;
        }}
        [data-testid="stMetricValue"] {{
            color: {THEME['accent']} !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {THEME['text_muted']} !important;
        }}

        /* ═══════════════════════════════════════════
           PROGRESS BARS — Animated gradient
           ═══════════════════════════════════════════ */
        .stProgress > div > div > div {{
            background: {THEME['gradient']} !important;
            border-radius: 8px !important;
            animation: shimmer 2s infinite linear;
            background-size: 200% 100%;
        }}
        @keyframes shimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}

        /* ═══════════════════════════════════════════
           FILE UPLOADER
           ═══════════════════════════════════════════ */
        [data-testid="stFileUploader"] {{
            background-color: {THEME['surface']};
            border: 1px dashed {THEME['border']};
            border-radius: 16px;
            padding: 1rem;
        }}
        [data-testid="stFileUploader"]:hover {{
            border-color: {THEME['accent']};
        }}

        /* ═══════════════════════════════════════════
           TABS
           ═══════════════════════════════════════════ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {THEME['surface']};
            border: 1px solid {THEME['border']};
            border-radius: 12px;
            color: {THEME['text_muted']};
            padding: 8px 20px;
            transition: all 0.3s ease;
        }}
        .stTabs [aria-selected="true"] {{
            background: {THEME['gradient']} !important;
            color: white !important;
            border: none !important;
        }}

        /* ═══════════════════════════════════════════
           DATAFRAMES & TABLES
           ═══════════════════════════════════════════ */
        [data-testid="stDataFrame"] {{
            border: 1px solid {THEME['border']};
            border-radius: 12px;
            overflow: hidden;
        }}

        /* ═══════════════════════════════════════════
           SCROLLBAR — Custom themed
           ═══════════════════════════════════════════ */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: {THEME['bg']};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {THEME['border']};
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {THEME['accent']};
        }}

        /* ═══════════════════════════════════════════
           CUSTOM COMPONENT CLASSES
           ═══════════════════════════════════════════ */
        .glass-card {{
            background: rgba(19, 19, 26, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid {THEME['border']};
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            hyphens: none !important;
            word-break: keep-all !important;
        }}
        .glass-card:hover {{
            border-color: {THEME['border_hover']};
            transform: translateY(-2px);
        }}

        .gradient-text {{
            background: {THEME['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .accent-badge {{
            display: inline-block;
            background: {THEME['gradient_subtle']};
            border: 1px solid {THEME['border']};
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 0.8rem;
            font-weight: 500;
            color: {THEME['accent']};
            font-family: 'JetBrains Mono', monospace;
        }}

        .feature-icon {{
            font-size: 2.5rem;
            margin-bottom: 0.8rem;
            display: block;
        }}

        .source-card {{
            background: rgba(19, 19, 26, 0.6);
            border: 1px solid {THEME['border']};
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }}
        .source-card:hover {{
            border-color: {THEME['accent']};
        }}

        .stat-number {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.8rem;
            font-weight: 700;
            background: {THEME['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .processing-step {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0;
            color: {THEME['text_muted']};
        }}
        .processing-step.active {{
            color: {THEME['accent']};
        }}
        .processing-step.done {{
            color: {THEME['success']};
        }}

        /* Animated gradient border for hero */
        .hero-border {{
            background: {THEME['gradient']};
            padding: 2px;
            border-radius: 24px;
            animation: borderGlow 3s ease-in-out infinite alternate;
        }}
        .hero-inner {{
            background: {THEME['surface']};
            border-radius: 22px;
            padding: 3rem;
        }}
        @keyframes borderGlow {{
            0% {{ box-shadow: 0 0 20px {THEME['accent_glow']}; }}
            100% {{ box-shadow: 0 0 40px rgba(6, 182, 212, 0.3); }}
        }}

        /* Pulse animation for processing */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .pulse {{
            animation: pulse 2s ease-in-out infinite;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )
