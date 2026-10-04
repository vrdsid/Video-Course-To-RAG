import whisper
import json
import os
import glob

def transcribe_all(audio_dir: str = "../data/raw/audio", output_dir: str = "../data/processed"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading Whisper 'base' model...")
    model = whisper.load_model("base") 
    
    # STRICT FILTER: Only grab files containing 'f251' (YouTube's audio-only format)
    media_files = glob.glob(os.path.join(audio_dir, "*f251*.webm"))
    
    if not media_files:
        print(f"No audio files found in {audio_dir}")
        return

    print(f"Found {len(media_files)} pure audio files. Starting transcription...")

    for file_path in media_files:
        base_name = os.path.basename(file_path).rsplit('.', 1)[0]
        output_file = os.path.join(output_dir, f"{base_name}_transcript.json")
        
        if os.path.exists(output_file):
            print(f"Skipping {base_name}, already transcribed.")
            continue
            
        print(f"\nTranscribing {base_name}...")
        
        try:
            result = model.transcribe(file_path)
            
            structured_data = []
            for segment in result["segments"]:
                structured_data.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })
                
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, indent=4)
                
            print(f"Saved transcript to {output_file}")
            
        except RuntimeError as e:
            print(f"WARNING: Skipping {base_name}. Could not extract audio.")
            continue

if __name__ == "__main__":
    transcribe_all()