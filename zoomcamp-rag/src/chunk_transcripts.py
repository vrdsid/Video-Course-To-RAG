import json
import os
import glob
from langchain_core.documents import Document

def chunk_transcripts_with_metadata(input_dir="../data/processed", chunk_duration_sec=75):
    """
    Reads Whisper JSON transcripts, groups them into logical time-based chunks,
    and attaches the start time and filename as metadata for the frontend video player.
    """
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    all_documents = []

    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return all_documents

    print(f"Processing {len(json_files)} transcript files...")

    for file_path in json_files:
        base_name = os.path.basename(file_path).replace("_transcript.json", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            segments = json.load(f)
            
        current_chunk_text = []
        chunk_start_time = 0.0
        
        for i, segment in enumerate(segments):
            if not current_chunk_text:
                chunk_start_time = segment["start"]
                
            current_chunk_text.append(segment["text"])
            
            # If the chunk spans more than 75 seconds, or it's the last segment, save it
            if segment["end"] - chunk_start_time >= chunk_duration_sec or i == len(segments) - 1:
                doc = Document(
                    page_content=" ".join(current_chunk_text),
                    metadata={
                        "source_file": base_name,
                        "start_time": chunk_start_time,
                        "end_time": segment["end"],
                        "source_type": "video"
                    }
                )
                all_documents.append(doc)
                current_chunk_text = [] # Reset for the next chunk

    print(f"Created {len(all_documents)} metadata-rich chunks ready for the Vector DB.")
    return all_documents

if __name__ == "__main__":
    docs = chunk_transcripts_with_metadata()
    if docs:
        print("\nSample Chunk Metadata:")
        print(json.dumps(docs[0].metadata, indent=4))
        print("\nSample Chunk Text:")
        print(docs[0].page_content[:200] + "...")