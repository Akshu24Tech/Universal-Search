# Universal Search — Multimodal RAG Engine

## Role

Act as a World-Class Senior AI/ML Engineer and Full-Stack Python Developer. You build high-fidelity, production-ready **Multimodal Retrieval-Augmented Generation (RAG)** applications. Every tool you produce should feel like a premium research instrument — seamless multimodal ingestion, intelligent vector retrieval, and crisp conversational answers grounded in real uploaded content. Eradicate all generic AI chatbot patterns.

---

## What This Tool Does

The user uploads **any combination** of:
- 📄 **PDFs** (research papers, notes, slides, manuals)
- 🎵 **Audio clips** (lectures, podcasts, meetings, voice memos)
- 🎬 **Videos** (tutorials, presentations, screen recordings)

The app:

1. **Ingests** each file — extracts text from PDFs, transcribes audio/video via Gemini, and pulls keyframes from video.
2. **Embeds** all extracted content into a unified vector space using **Gemini's interleaved multimodal embeddings** — text, images, and audio concepts fused into single vectors.
3. **Indexes** all vectors in a local **ChromaDB** (or FAISS) collection for lightning-fast retrieval.
4. **Answers** user questions by retrieving the most relevant chunks across ALL uploaded media and generating grounded, cited responses via Gemini.

**The "Power Move":** This app uses `gemini-embedding-2-preview`'s interleaved embedding capability — combining text descriptions AND visual/audio context into single vectors. This is NOT standard text-only RAG. This is multimodal fusion RAG.

---

## Agent Flow — MUST FOLLOW

When the user asks to build this app (or this file is loaded into a fresh project), immediately ask **exactly these questions** in a single call, then build the full app from the answers. Do not ask follow-ups. Do not over-discuss. Build.

### Questions (all in one call)

1. **"What's your primary use case for Universal Search?"**
   Single-select:
   - A) Academic research — searching across papers, lecture recordings, and video tutorials
   - B) Meeting intelligence — searching across meeting recordings, transcripts, and shared documents
   - C) Content creation — searching across reference materials, interviews, and b-roll footage
   - D) General-purpose (all of the above)

2. **"Which vector database do you prefer?"**
   Single-select:
   - A) **ChromaDB** — persistent, metadata-rich, great for prototyping (recommended)
   - B) **FAISS** — Facebook's blazing-fast similarity search, pure in-memory
   - C) Both (user picks per session)

3. **"Should the app support real-time streaming answers?"**
   Yes / No — if Yes, Gemini responses stream token-by-token for a ChatGPT-like feel.

4. **"Pick a UI theme"**
   - A) **"Neural Dark"** — Deep space black, electric violet accents, glassmorphism cards. Feels like a research command center (Arc/Raycast aesthetic).
   - B) **"Scholar Light"** — Warm ivory, deep navy text, amber highlights. Feels like a digital research library (Notion/Readwise aesthetic).
   - C) **"Matrix"** — Pure black, phosphor green, monospace everything. Hacker/researcher aesthetic.

---

## Technology Stack (NEVER CHANGE)

| Layer | Technology |
|---|---|
| **UI Framework** | [Streamlit](https://streamlit.io/) (latest) |
| **LLM / Embeddings** | [google-generativeai](https://pypi.org/project/google-generativeai/) SDK — `gemini-embedding-2-preview` for embeddings, `gemini-2.0-flash` (or latest) for generation |
| **Vector DB (Option A)** | [ChromaDB](https://www.trychroma.com/) with persistent storage |
| **Vector DB (Option B)** | [FAISS](https://github.com/facebookresearch/faiss) (`faiss-cpu`) |
| **PDF Extraction** | [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) — text + image extraction |
| **Audio Transcription** | Gemini API (upload audio file → extract text via `generate_content`) |
| **Video Processing** | [OpenCV](https://opencv.org/) (`cv2`) for keyframe extraction + Gemini API for visual understanding |
| **Image Handling** | [Pillow](https://python-pillow.org/) (PIL) |
| **Chunking** | Custom recursive text splitter (configurable chunk size / overlap) |
| **Environment** | [python-dotenv](https://pypi.org/project/python-dotenv/) for API key management |
| **Data Handling** | [NumPy](https://numpy.org/) for vector operations |

**Install command:**
```bash
pip install streamlit google-generativeai chromadb faiss-cpu pymupdf opencv-python-headless Pillow python-dotenv numpy
```

**Run command:**
```bash
streamlit run app.py
```

---

## UI Theme Design Systems

### Theme A — "Neural Dark"
- **Background:** `#0A0A0F` (deep space)
- **Surface:** `#13131A` (dark card) with `backdrop-filter: blur(20px)` glassmorphism
- **Accent Primary:** `#8B5CF6` (electric violet)
- **Accent Secondary:** `#06B6D4` (cyan spark)
- **Gradient:** `linear-gradient(135deg, #8B5CF6, #06B6D4)` for key CTAs
- **Text Primary:** `#F1F5F9`
- **Text Muted:** `#64748B`
- **Border:** `rgba(139, 92, 246, 0.15)` (violet glow border)
- **Font:** "Inter" (UI), "JetBrains Mono" (data/code/metrics)
- **Feel:** Arc browser, Raycast, Linear — futuristic research tool

### Theme B — "Scholar Light"
- **Background:** `#FEFCF3` (warm ivory)
- **Surface:** `#FFFFFF` with subtle `box-shadow: 0 1px 3px rgba(0,0,0,0.08)`
- **Accent Primary:** `#1E3A5F` (deep navy)
- **Accent Secondary:** `#D97706` (warm amber)
- **Text Primary:** `#1C1917`
- **Text Muted:** `#78716C`
- **Border:** `#E7E5E4`
- **Font:** "Lora" (headings), "Inter" (body), "IBM Plex Mono" (code/data)
- **Feel:** Notion, Readwise, academic journal — trustworthy and elegant

### Theme C — "Matrix"
- **Background:** `#000000`
- **Surface:** `#0A0A0A`
- **Accent Primary:** `#22C55E` (phosphor green)
- **Accent Secondary:** `#16A34A` (deeper green)
- **Text Primary:** `#22C55E`
- **Text Muted:** `#166534`
- **Border:** `#14532D`
- **Font:** "Space Mono" (everything)
- **Feel:** Terminal, tmux, hacker tools — raw and powerful

---

## Core Architecture — The Multimodal RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     UNIVERSAL SEARCH ENGINE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                     │
│  │   PDF    │   │  AUDIO   │   │  VIDEO   │   ← File Upload     │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘                     │
│       │              │              │                           │
│       ▼              ▼              ▼                           │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐                 │
│  │ PyMuPDF  │   │ Gemini   │   │ OpenCV +     │   ← Extract     │
│  │ Extract  │   │ Transcr. │   │ Gemini Desc. │                 │
│  └────┬─────┘   └────┬─────┘   └──────┬───────┘                 │
│       │              │                 │                        │
│       ▼              ▼                 ▼                        │
│  ┌─────────────────────────────────────────────┐                │
│  │     CHUNKING ENGINE                         │                │
│  │  (Recursive text splitter + metadata tags)  │   ← Chunk      │
│  └──────────────────┬──────────────────────────┘                │
│                     │                                           │
│                     ▼                                           │
│  ┌─────────────────────────────────────────────┐                │
│  │     GEMINI EMBEDDING ENGINE                 │                │
│  │  model: gemini-embedding-2-preview          │                │
│  │  task_type: RETRIEVAL_DOCUMENT              │                │
│  │  ★ Interleaved: text + image → ONE vector  │   ← Embed      │
│  └──────────────────┬──────────────────────────┘                │
│                     │                                           │
│                     ▼                                           │
│  ┌─────────────────────────────────────────────┐                │
│  │     VECTOR DATABASE                         │                │
│  │  ChromaDB (persistent) / FAISS (in-memory)  │   ← Store      │
│  └──────────────────┬──────────────────────────┘                │
│                     │                                           │
│                     ▼                                           │
│  ┌─────────────────────────────────────────────┐                │
│  │     QUERY PIPELINE                          │                │
│  │  1. Embed user query (RETRIEVAL_QUERY)      │                │
│  │  2. Retrieve top-K relevant chunks          │                │
│  │  3. Build grounded prompt with citations    │   ← Retrieve   │
│  │  4. Generate answer via Gemini              │                │
│  └─────────────────────────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## App Architecture — Component by Component

### 1. SIDEBAR — "The Control Center"
Streamlit sidebar with:
- **App logo + title** ("Universal Search 🔍")
- **API Key input** (password field, validates on entry, stored in `st.session_state`)
- **File uploader** — multi-file, accepts: `.pdf`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`
- **Uploaded files list** — shows file name, type icon (📄🎵🎬), file size, processing status badge
- **Vector DB selector** — radio: ChromaDB / FAISS
- **Settings expander:**
  - Chunk size slider (200–2000 tokens, default 500)
  - Chunk overlap slider (0–200 tokens, default 50)
  - Top-K results slider (1–20, default 5)
  - Temperature slider (0.0–1.0, default 0.3)
  - Model selector for generation (gemini-2.0-flash / gemini-2.5-pro)
- **"Process All Files"** button — triggers the full ingestion pipeline
- **"Clear Knowledge Base"** button — wipes vector store + session state
- **Session stats:** Total chunks indexed, files processed, DB size

### 2. MAIN AREA — "The Search Interface"
Center-stage conversational interface:

#### State: No Files Processed
- Full-width **hero section**:
  - Large animated icon (search + document + waveform composition)
  - Headline: "Drop any PDF, Audio, or Video — then ask anything."
  - Subtext: "Universal Search uses multimodal AI to understand and connect information across all your files."
  - Three feature cards in a row:
    - 📄 "PDFs" — "Extract text, tables, and images from documents"
    - 🎵 "Audio" — "Transcribe and search spoken content"
    - 🎬 "Video" — "Extract keyframes and narration from videos"
  - Animated gradient border on the hero card

#### State: Processing
- **Processing dashboard** replaces hero:
  - Per-file progress cards showing:
    - File name + type icon
    - Current processing step (Extracting → Chunking → Embedding → Indexing)
    - Progress bar (animated gradient shimmer)
    - Step completion checkmarks
  - Overall pipeline progress bar at top
  - Live stats: "Extracted 2,450 words from lecture.mp3..."

#### State: Ready (Files Indexed)
- **Chat interface** with:
  - Scrollable message history (user questions + AI answers)
  - Each AI answer shows:
    - The generated response (markdown-formatted)
    - **Source citations** — expandable cards showing:
      - Source file name + type icon
      - Chunk text snippet (highlighted relevant portion)
      - Relevance score (cosine similarity %)
      - For video: timestamp of the keyframe
      - For audio: approximate time range in the recording
  - **Query input** — wide text input at bottom with send button
  - **Suggested questions** — 3-4 auto-generated starter questions based on indexed content

### 3. KNOWLEDGE BASE EXPLORER — "The X-Ray"
Expandable panel (Streamlit expander or tab) showing:
- **All indexed chunks** in a searchable/filterable table:
  - Chunk ID, source file, content preview, modality type, token count
- **Chunk distribution** — pie chart showing chunks per file / per modality
- **Embedding visualization** — 2D t-SNE/UMAP plot of all vectors (colored by source file) using `plotly`
- **Raw text viewer** — select a file to see its full extracted text

### 4. PROCESSING LOG — "The Audit Trail"
Collapsible panel showing:
- Timestamped log of every processing step
- Errors and warnings (with file name context)
- Performance metrics:
  - Extraction time per file
  - Embedding time per batch
  - Total indexing time
  - Query latency

---

## Multimodal Ingestion Pipeline — Detailed

### PDF Processing (`processors/pdf_processor.py`)
```python
# 1. Open PDF with PyMuPDF (fitz)
# 2. For each page:
#    a. Extract text blocks with positions
#    b. Extract embedded images
#    c. Detect tables (heuristic: aligned text blocks)
# 3. Combine text + image descriptions into chunks
# 4. Metadata: {source: filename, page: N, type: "pdf", has_images: bool}
```

### Audio Processing (`processors/audio_processor.py`)
```python
# 1. Upload audio file to Gemini API
# 2. Use generate_content to transcribe:
#    prompt = "Transcribe this audio completely. Include timestamps every 30 seconds."
# 3. Parse transcript into time-stamped segments
# 4. Chunk segments by time window (configurable)
# 5. Metadata: {source: filename, type: "audio", time_start: "MM:SS", time_end: "MM:SS"}
```

### Video Processing (`processors/video_processor.py`)
```python
# 1. Extract keyframes using OpenCV:
#    - Sample every N seconds (configurable, default: 10s)
#    - Or use scene-change detection (frame diff > threshold)
# 2. Extract audio track → process as audio (transcription)
# 3. For each keyframe:
#    - Send to Gemini: "Describe what's shown in this frame in detail."
#    - Generate interleaved embedding: [description_text, keyframe_image]
# 4. Combine visual descriptions + transcript into chunks
# 5. Metadata: {source: filename, type: "video", timestamp: "MM:SS", has_keyframe: bool}
```

### Interleaved Embedding — The Core Innovation
```python
import google.generativeai as genai
import PIL.Image

# Standard text embedding
text_result = genai.embed_content(
    model='models/gemini-embedding-2-preview',
    content="NAND gate implementation for digital circuits",
    task_type="RETRIEVAL_DOCUMENT"
)

# ★ INTERLEAVED embedding — text + image fused into ONE vector
img = PIL.Image.open('circuit_diagram.png')
description = "Circuit diagram showing a NAND gate implementation"

interleaved_result = genai.embed_content(
    model='models/gemini-embedding-2-preview',
    content=[description, img],  # Mixed input!
    task_type="RETRIEVAL_DOCUMENT"
)

# For queries
query_result = genai.embed_content(
    model='models/gemini-embedding-2-preview',
    content="How does the NAND gate work?",
    task_type="RETRIEVAL_QUERY"
)
```

---

## Query Pipeline — Detailed

### Step 1: Query Embedding
```python
query_embedding = genai.embed_content(
    model='models/gemini-embedding-2-preview',
    content=user_query,
    task_type="RETRIEVAL_QUERY"
)['embedding']
```

### Step 2: Retrieval
```python
# ChromaDB
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    include=["documents", "metadatas", "distances"]
)

# FAISS
distances, indices = index.search(
    np.array([query_embedding], dtype='float32'),
    top_k
)
```

### Step 3: Grounded Prompt Construction
```python
context_prompt = """You are Universal Search, an AI research assistant.
Answer the user's question using ONLY the provided context from their uploaded files.

RULES:
- Cite your sources using [Source: filename, page/timestamp] format
- If the answer spans multiple sources, synthesize and cite each
- If you cannot find the answer in the context, say so clearly
- Be specific and detailed in your answers

CONTEXT:
{retrieved_chunks_with_metadata}

USER QUESTION: {user_query}
"""
```

### Step 4: Generation
```python
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content(context_prompt, stream=True)
# Stream tokens to Streamlit UI
```

---

## File Structure

```
universal-search/
├── app.py                          # Main Streamlit application
├── .env                            # API keys (gitignored)
├── .env.example                    # Template for .env
├── requirements.txt                # All dependencies
├── README.md                       # Project documentation
│
├── core/
│   ├── __init__.py
│   ├── embedder.py                 # Gemini embedding engine (interleaved support)
│   ├── chunker.py                  # Recursive text splitter
│   ├── vector_store.py             # ChromaDB / FAISS abstraction layer
│   └── query_engine.py             # RAG query pipeline (retrieve + generate)
│
├── processors/
│   ├── __init__.py
│   ├── pdf_processor.py            # PDF text + image extraction
│   ├── audio_processor.py          # Audio transcription via Gemini
│   └── video_processor.py          # Keyframe extraction + transcription
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py                  # Sidebar component (upload, settings, stats)
│   ├── chat_interface.py           # Chat UI with citations
│   ├── hero_section.py             # Empty state hero
│   ├── processing_dashboard.py     # Processing progress UI
│   ├── knowledge_explorer.py       # Chunk browser + embedding viz
│   └── theme.py                    # Theme tokens + custom CSS injection
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py               # File type detection, temp storage
│   └── logging_utils.py            # Processing log management
│
├── assets/
│   └── logo.svg                    # App logo
│
└── data/
    └── chroma_db/                  # Persistent ChromaDB storage (gitignored)
```

---

## Streamlit Custom Theming — CSS Injection

Since Streamlit has limited native theming, inject custom CSS via `st.markdown()`:

```python
def inject_theme(theme_name: str):
    """Inject custom CSS for the selected theme."""
    themes = {
        "neural_dark": {
            "bg": "#0A0A0F",
            "surface": "#13131A",
            "accent": "#8B5CF6",
            "accent2": "#06B6D4",
            "text": "#F1F5F9",
            "muted": "#64748B",
            "border": "rgba(139, 92, 246, 0.15)",
            "font": "'Inter', sans-serif",
            "mono": "'JetBrains Mono', monospace",
        },
        # ... other themes
    }
    t = themes[theme_name]
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Global */
        .stApp {{
            background-color: {t['bg']};
            font-family: {t['font']};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {t['surface']};
            border-right: 1px solid {t['border']};
        }}
        
        /* Cards / Containers */
        [data-testid="stExpander"] {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 16px;
        }}
        
        /* Accent buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {t['accent']}, {t['accent2']});
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px {t['accent']}40;
        }}
        
        /* Chat messages */
        [data-testid="stChatMessage"] {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 1rem;
        }}
        
        /* Metrics */
        [data-testid="stMetric"] {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 1rem;
        }}
        
        /* Text input */
        .stTextInput > div > div > input {{
            background-color: {t['surface']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 12px;
        }}
        
        /* Progress bars */
        .stProgress > div > div > div {{
            background: linear-gradient(90deg, {t['accent']}, {t['accent2']});
            border-radius: 8px;
        }}
        
        /* Noise overlay for premium feel */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 1;
        }}
    </style>
    """, unsafe_allow_html=True)
```

---

## Design System — Fixed Rules (NEVER CHANGE)

- **Noise overlay:** CSS pseudo-element SVG noise at 0.04 opacity — eliminates flat digital feel.
- **Radius system:** All cards and containers use `border-radius: 16px` minimum. Hero sections use `24px`.
- **Transitions:** All interactive elements use `transition: all 0.3s ease`.
- **Hover states:** Buttons lift `translateY(-2px)` with accent glow shadow on hover.
- **Progress indicators:** Animated gradient shimmer (accent → accent2) while processing.
- **Glassmorphism:** Surface elements use backdrop blur + semi-transparent backgrounds for depth.
- **Empty states:** Always show an illustrated icon composition — never a blank area.
- **Citations:** Every AI answer MUST show source cards with file name, type, and content excerpt.
- **Metrics:** Use Streamlit metric cards with custom styling for stats (chunks, files, latency).
- **Animations:** Use Streamlit's native spinner + progress bar, enhanced with CSS transitions.

---

## Build Sequence

After receiving answers to the 4 questions:

1. Map the selected theme to its full design tokens.
2. Create project directory + install all deps.
3. Build in this order:
   - `.env.example` — template with `GOOGLE_API_KEY=your_key_here`
   - `requirements.txt` — all dependencies pinned
   - `core/embedder.py` — Gemini embedding engine with interleaved support
   - `core/chunker.py` — recursive text splitter
   - `core/vector_store.py` — ChromaDB / FAISS abstraction
   - `core/query_engine.py` — RAG pipeline (embed query → retrieve → generate)
   - `processors/pdf_processor.py` — PyMuPDF extraction
   - `processors/audio_processor.py` — Gemini transcription
   - `processors/video_processor.py` — OpenCV keyframes + Gemini descriptions
   - `ui/theme.py` — CSS injection for selected theme
   - `ui/sidebar.py` — sidebar with upload + settings
   - `ui/hero_section.py` — empty state hero
   - `ui/processing_dashboard.py` — processing progress UI
   - `ui/chat_interface.py` — conversational interface with citations
   - `ui/knowledge_explorer.py` — chunk browser + visualization
   - `app.py` — main orchestrator assembling all components
4. Wire end-to-end: upload → extract → chunk → embed → index → query → answer → cite.
5. Test with a mental walkthrough: upload a PDF + audio → ask a cross-modal question → verify cited answer.

---

## Example Cross-Modal Query

**Uploaded files:**
- `machine_learning_textbook.pdf` (Chapter on Neural Networks)
- `lecture_recording.mp3` (Professor explaining backpropagation)
- `tutorial_video.mp4` (Coding a neural network from scratch)

**User query:** "How does backpropagation update the weights?"

**Expected answer:**
> Backpropagation updates weights by computing the gradient of the loss function with respect to each weight using the chain rule. The gradient flows backward through the network, layer by layer...
>
> **Sources:**
> - 📄 `machine_learning_textbook.pdf` (Page 142) — "The backpropagation algorithm computes ∂L/∂w for each weight w..."
> - 🎵 `lecture_recording.mp3` (12:30–13:45) — "...so the key insight is that we propagate the error backwards..."
> - 🎬 `tutorial_video.mp4` (08:15) — [Keyframe showing code: `weight -= learning_rate * gradient`]

---

## Execution Directive

"Do not build a chatbot with a file upload. Build a multimodal research instrument. Every file type should be ingested transparently. Every answer should be grounded and cited. Every interaction should feel like querying a personal research assistant that has actually read, listened to, and watched everything you gave it."
