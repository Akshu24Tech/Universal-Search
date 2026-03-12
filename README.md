# 🔍 Universal Search — Multimodal RAG Engine

A premium multimodal Retrieval-Augmented Generation (RAG) application for academic research. Upload PDFs, audio recordings, and videos — then ask questions across all your research materials.

## ✨ Features

- **📄 PDF Processing** — Extract text, tables, and images from research papers
- **🎵 Audio Transcription** — Transcribe lectures, podcasts, and meetings via Gemini
- **🎬 Video Analysis** — Extract keyframes + narration from tutorials and presentations
- **🧬 Interleaved Embeddings** — Fuse text + images into unified vectors using `gemini-embedding-2-preview`
- **💾 Dual Vector Store** — Choose ChromaDB (persistent) or FAISS (in-memory) per session
- **⚡ Streaming Answers** — Real-time token-by-token responses grounded in your files
- **📚 Source Citations** — Every answer includes cited sources with relevance scores
- **🧠 Knowledge Explorer** — Browse chunks, view distribution charts, and visualize embeddings

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

Or enter it directly in the app sidebar.

### 3. Run
```bash
streamlit run app.py
```

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| LLM & Embeddings | Gemini API (`gemini-embedding-2-preview`, `gemini-2.0-flash`) |
| Vector DB | ChromaDB + FAISS |
| PDF | PyMuPDF |
| Audio/Video | Gemini API + OpenCV |
| Visualization | Plotly + scikit-learn (t-SNE) |

## 📁 Project Structure

```
universal-search/
├── app.py                    # Main Streamlit application
├── core/
│   ├── embedder.py           # Gemini embedding engine
│   ├── chunker.py            # Recursive text splitter
│   ├── vector_store.py       # ChromaDB / FAISS abstraction
│   └── query_engine.py       # RAG query pipeline
├── processors/
│   ├── pdf_processor.py      # PDF extraction
│   ├── audio_processor.py    # Audio transcription
│   └── video_processor.py    # Video keyframe + transcription
├── ui/
│   ├── theme.py              # Neural Dark theme
│   ├── sidebar.py            # Control center
│   ├── hero_section.py       # Empty state hero
│   ├── processing_dashboard.py
│   ├── chat_interface.py     # Chat with citations
│   └── knowledge_explorer.py # Chunk browser + viz
└── utils/
    ├── file_utils.py         # File utilities
    └── logging_utils.py      # Processing log
```

## 🎨 Theme: Neural Dark

Deep space black background, electric violet + cyan accents, glassmorphism cards, animated gradient borders, and a subtle noise overlay for premium texture.
