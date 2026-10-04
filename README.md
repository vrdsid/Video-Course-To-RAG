# 📺 Data Engineering Zoomcamp AI Assistant

A local, lightning-fast RAG (Retrieval-Augmented Generation) application built to navigate, query, and synthesize the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) curriculum. 

This assistant runs a localized LLM to parse course transcripts and GitHub notes, streaming step-by-step answers while perfectly syncing a YouTube player to the exact timestamp the information is mentioned.

## 🚀 App Demo

https://github.com/user-attachments/assets/246d0785-b154-423b-af79-58e432d7c763

## 🎯 The Use Case

**The Problem:** The Data Engineering Zoomcamp contains dozens of hours of video lectures and hundreds of pages of GitHub markdown notes. When a student gets stuck or needs to review a specific concept, manually scrubbing through YouTube videos or searching across multiple repositories is incredibly time-consuming.

**The Solution:** This project acts as an autonomous, localized Teaching Assistant. A user asks a natural language question, and the system searches a vector database, reads the specific transcripts and notes, and streams a summarized, step-by-step answer. It proves its work by providing clickable citations that instantly play the exact second of the YouTube video where the instructor explains it, or scrolls directly to the exact paragraph in the GitHub repository.

## 📂 Folder & File Structure

This is the architectural layout of the pipeline, separating the raw data, the database, and the active code.

```text
Video-Course-To-RAG/
├── .gitignore               # Keeps the repo clean by blocking heavy video/DB files
├── README.md                # Project documentation and setup instructions
├── assets/                  
│   └── demo.mp4             # Visual proof of the application working
├── data/                    # The Data Layer (Excluded from GitHub)
│   ├── raw/                 
│   │   ├── audio/           # Downloaded YouTube .webm audio files
│   │   └── github/          # Scraped markdown files from the Zoomcamp repo
│   ├── processed/           # Cleaned, chunked text files ready for embedding
│   └── qdrant_db/           # The compiled local Qdrant Vector Database
└── src/                     # The Application Layer
    ├── app.py                   
    ├── build_vector_db.py       
    ├── chunk_transcripts.py     
    ├── scrape_github.py         
    └── transcribe_whisper.py    
```

## 📄 The Data Pipeline & File Purposes

The project is divided into two phases: **Data Ingestion** (Scripts) and **Data Serving** (`app.py`).

**1. The Ingestion Pipeline (`src/` background scripts):**
*   **`scrape_github.py`**: Crawls the official DataTalksClub GitHub repository and downloads the course notes and instructions as raw text.
*   **`transcribe_whisper.py`**: Takes the downloaded YouTube audio files and uses OpenAI's Whisper model to transcribe the spoken words into text, mapping every sentence to its exact start time in seconds.
*   **`chunk_transcripts.py`**: Breaks the massive transcript and markdown files into smaller, overlapping chunks (paragraphs) so the AI can read them in bite-sized pieces without losing context.
*   **`build_vector_db.py`**: Converts those text chunks into mathematical vectors using HuggingFace (`all-MiniLM-L6-v2`) and loads them into the local Qdrant database for lightning-fast semantic search.

**2. The Serving Application (`src/app.py`):**
This is the heart of the project. When a user runs this file, it handles:
*   **The UI:** Renders the Streamlit frontend.
*   **The Search:** Takes the user's question, converts it to a vector, and pulls the top 8 most mathematically relevant chunks from Qdrant (`similarity_search_with_score`).
*   **The LLM Orchestration:** Wraps the retrieved context and the user's question in a strict System Prompt designed to prevent hallucinations and prompt injection, then sends it to the local `llama3.2:1b` model.
*   **The Media Routing:** Uses Regex to extract the YouTube ID from the database metadata and dynamically embeds the official YouTube player cued to the exact timestamp, alongside auto-scrolling GitHub links.

## ✨ Key Features

* **100% Local & Free:** Powered by Llama 3.2:1B via Ollama. No API keys, zero cloud LLM costs.
* **YouTube Time-Sync:** Extracts video IDs from chunks and embeds the official YouTube player cued to the exact second of relevance.
* **Auto-Scrolling Source Links:** GitHub citations use Text Fragments to instantly highlight the exact paragraph the LLM read.
* **Strict Anti-Hallucination:** System prompts are engineered with strict context-boundaries and fail-safes for off-topic questions.
* **Prompt Injection Defenses:** Implements UI character limits, XML delimiters, and System/Human role segregation.
* **Lightning Fast:** Uses LLM text-streaming and native browser video embedding for zero-lag performance.

## 🛠️ Tech Stack

* **UI:** Streamlit
* **Local LLM:** Ollama (Llama 3.2:1B)
* **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
* **Vector Database:** Qdrant
* **Orchestration:** LangChain

## 💻 Local Setup

**1. Install Prerequisites**
* Python 3.10+
* [Ollama](https://ollama.com/download)

**2. Pull the Local Model**
```bash
ollama pull llama3.2:1b
```

**3. Clone & Install Dependencies**
```bash
git clone [https://github.com/vrdsid/zoomcamp-video-rag.git](https://github.com/vrdsid/zoomcamp-video-rag.git)
cd zoomcamp-video-rag
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

**4. Launch the App**
```bash
streamlit run src/app.py
```

## ⚠️ Disclaimer

This project was built purely as a learning exercise and a supplementary tool for students navigating the course. I do not claim ownership of any course materials. All credit for the Data Engineering Zoomcamp curriculum, videos, and notes belongs to [Alexey Grigorev](https://github.com/alexeygrigorev) and the [DataTalks.Club](https://datatalks.club/) community. This project is not officially affiliated with the course, and there is no intention of copyright infringement.
