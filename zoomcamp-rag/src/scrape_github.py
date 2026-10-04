import os
import requests
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# URLs for the official Zoomcamp Markdown notes
GITHUB_URLS = [
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/README.md",
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/01-docker-terraform/README.md",
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/02-workflow-orchestration/README.md",
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/03-data-warehouse/README.md",
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/04-analytics-engineering/README.md",
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/05-batch/README.md",
    "https://raw.githubusercontent.com/DataTalksClub/data-engineering-zoomcamp/main/06-streaming/README.md"
]

def process_github_notes():
    os.makedirs("../data/raw/github", exist_ok=True)
    documents = []
    splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)

    print("Downloading and chunking GitHub notes...")
    for url in GITHUB_URLS:
        response = requests.get(url)
        if response.status_code == 200:
            # Extract a readable filename from the URL
            folder = url.split("/")[-2]
            filename = f"{folder}_notes.md" if folder != "data-engineering-zoomcamp" else "Course_Overview.md"
            
            filepath = f"../data/raw/github/{filename}"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Chunk the markdown text
            chunks = splitter.split_text(response.text)
            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={"source_file": filename, "source_type": "github"}
                )
                documents.append(doc)

    print(f"Created {len(documents)} GitHub chunks. Adding to Qdrant...")
    
    # Load existing database
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    client = QdrantClient(path="../data/qdrant_db")
    qdrant = QdrantVectorStore(client=client, collection_name="zoomcamp_video_rag", embedding=embeddings)
    
    # Add the GitHub docs
    qdrant.add_documents(documents)
    print("Success! GitHub notes are now embedded in your Vector Database.")

if __name__ == "__main__":
    process_github_notes()