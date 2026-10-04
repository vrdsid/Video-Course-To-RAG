import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from chunk_transcripts import chunk_transcripts_with_metadata

def build_qdrant_db():
    print("Loading video chunks...")
    docs = chunk_transcripts_with_metadata()
    
    if not docs:
        print("No documents found to embed.")
        return

    print("Loading Embedding Model (all-MiniLM-L6-v2)...")
    # This model outputs vectors with 384 dimensions
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    db_path = "../data/qdrant_db"
    collection_name = "zoomcamp_video_rag"

    print(f"Initializing local Qdrant database at {db_path}...")
    client = QdrantClient(path=db_path)
    
    # Create the collection schema if it doesn't exist
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    print(f"Embedding and storing {len(docs)} chunks... This will take a few minutes on CPU.")
    
    # Connect LangChain to Qdrant and insert the documents
    qdrant = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    
    qdrant.add_documents(docs)
    print("Success! All video chunks have been vectorized and saved to the local database.")

if __name__ == "__main__":
    build_qdrant_db()