import streamlit as st
import os
import re
import urllib.parse
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Set page to wide mode
st.set_page_config(layout="wide", page_title="Zoomcamp AI Assistant")

# Resolve absolute paths based on this script's directory (src/)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "qdrant_db")

@st.cache_resource
def load_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    client = QdrantClient(path=DB_PATH)
    return QdrantVectorStore(
        client=client, 
        collection_name="zoomcamp_video_rag", 
        embedding=embeddings
    )

@st.cache_resource
def load_local_llm():
    return ChatOllama(model="llama3.2:1b", temperature=0)

def extract_youtube_id(filename):
    """Extracts the 11-character YouTube ID from between the brackets."""
    match = re.search(r'\[(.*?)\]', filename)
    if match:
        return match.group(1)
    return None

def stream_parser(stream):
    for chunk in stream:
        yield chunk.content

db = load_vector_db()
llm = load_local_llm()

# --- 🧠 SESSION STATE (MEMORY) ---
if 'last_query' not in st.session_state:
    st.session_state['last_query'] = ""
if 'last_answer' not in st.session_state:
    st.session_state['last_answer'] = ""
if 'last_sources' not in st.session_state:
    st.session_state['last_sources'] = []
if 'current_video' not in st.session_state:
    st.session_state['current_video'] = None
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = 0

st.title("📺 Data Engineering Zoomcamp AI Assistant")

col1, col2 = st.columns([1.2, 0.8])

with col1:
    query = st.text_input(
        "Ask a question:", 
        placeholder="e.g. Give me a step-by-step guide to complete Module 1",
        max_chars=200
    )
    
    if query:
        if query != st.session_state['last_query']:
            with st.spinner("Searching database..."):
                raw_results = db.similarity_search_with_score(query, k=8)
                sorted_results = sorted(raw_results, key=lambda x: x[1], reverse=True)
                st.session_state['last_sources'] = sorted_results
                
            if sorted_results:
                combined_context = "\n\n---\n\n".join([doc.page_content for doc, score in sorted_results])
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a helpful Data Engineering course assistant. 
                    Your task is to answer the user's question using ONLY the provided Context.

                    Context:
                    <context>
                    {context}
                    </context>

                    Instructions:
                    - Read the Context carefully and extract the answer.
                    - Explain it cleanly and clearly.
                    - If the Context does NOT contain the answer, you must output exactly: "I could not find enough detail in the provided course materials to answer that."
                    - Do not use outside knowledge or general information.
                    - Format any step-by-step instructions as numbered lists.
                    """),
                    ("human", "Question: {question}")
                ])
                
                st.subheader("💡 Answer")
                chain = prompt | llm
                
                response_stream = chain.stream({"context": combined_context, "question": query})
                full_answer = st.write_stream(stream_parser(response_stream))
                
                st.session_state['last_query'] = query
                st.session_state['last_answer'] = full_answer

            else:
                st.warning("No relevant content located in the database.")
                st.session_state['last_query'] = query
                st.session_state['last_answer'] = "No relevant content located."
                st.session_state['last_sources'] = []

        else:
            st.subheader("💡 Answer")
            st.markdown(st.session_state['last_answer'])
        
        # --- RENDER SOURCES ---
        if st.session_state['last_sources']:
            st.subheader("📚 Sources Referenced (Sorted by Relevance)")
            
            for doc, score in st.session_state['last_sources']:
                source_file = doc.metadata.get('source_file', 'Unknown')
                source_type = doc.metadata.get('source_type', 'video')
                
                relevance_pct = f"{score * 100:.1f}%"
                
                if source_type == "github":
                    # Point directly to the main branch of your Zoomcamp repository
                    base_github_url = "https://github.com/vrdsid/Data-Engineering-ZoomCamp-2026/blob/main"
                    clean_path = source_file.replace("\\", "/")
                    
                    # Extract the first 6 words of the chunk to use as a browser scroll target
                    snippet = " ".join(doc.page_content.split()[:6])
                    encoded_snippet = urllib.parse.quote(snippet)
                    
                    # Append the Text Fragment syntax to jump directly to the paragraph
                    github_url = f"{base_github_url}/{clean_path}#:~:text={encoded_snippet}"
                    
                    st.markdown(f"📄 **GitHub Guide:** [{source_file}]({github_url}) *(Relevance: {relevance_pct})*")
                    
                elif source_type == "video":
                    time_sec = int(doc.metadata.get('start_time', 0))
                    button_label = f"▶️ {source_file[:35]}... at {time_sec}s (Relevance: {relevance_pct})"
                    
                    if st.button(button_label, key=f"{source_file}_{time_sec}"):
                        st.session_state['current_video'] = source_file
                        st.session_state['start_time'] = time_sec

with col2:
    st.header("Video Player")
    if st.session_state['current_video']:
        video_name = st.session_state['current_video']
        start_time = st.session_state['start_time']
        
        video_id = extract_youtube_id(video_name)
        
        if video_id:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            st.success(f"Playing from **{start_time} seconds**")
            
            st.video(youtube_url, start_time=start_time)
            
            st.caption(f"*Streaming directly from YouTube (ID: {video_id})*")
        else:
            st.error(f"Could not extract a valid YouTube ID from: {video_name}")
    else:
        st.markdown("👈 *Click any video timestamp on the left to cue the visual player.*")