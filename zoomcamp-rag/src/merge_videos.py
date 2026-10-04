import os
import glob
import subprocess
import re
import shutil

def merge_media():
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))
    
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw", "audio")
    merged_dir = os.path.join(PROJECT_ROOT, "data", "raw", "merged_videos")
    os.makedirs(merged_dir, exist_ok=True)

    print("1. Cleaning up corrupted files from previous runs...")
    for f in glob.glob(os.path.join(merged_dir, "*.webm")):
        # If the file is less than 1MB, it's corrupted/empty. Delete it.
        if os.path.getsize(f) < (1024 * 1024): 
            os.remove(f)
            print(f"   Deleted broken file: {os.path.basename(f)}")

    print("\n2. Processing Media...")
    audio_files = glob.glob(os.path.join(raw_dir, "*f251*.webm"))
    
    for audio_path in audio_files:
        match = re.search(r'\[(.*?)\]', os.path.basename(audio_path))
        if not match: continue
        video_id = match.group(1)
        
        # Look for a matching video file
        possible_videos = glob.glob(os.path.join(raw_dir, f"*{video_id}*.webm")) + \
                          glob.glob(os.path.join(raw_dir, f"*{video_id}*.mp4"))
        
        video_files = [f for f in possible_videos if 'f251' not in f]
        
        # Clean up the output filename
        clean_name = os.path.basename(audio_path).replace('.f251', '').replace('-12', '').replace('-16', '').replace('-17', '').replace('-19', '').replace('-5', '').replace('-1', '')
        out_path = os.path.join(merged_dir, clean_name)
        
        if os.path.exists(out_path):
            continue
            
        if video_files:
            # We have both! Merge them.
            video_path = video_files[0]
            print(f"Merging Video + Audio: {clean_name}")
            cmd = ['ffmpeg', '-y', '-i', video_path, '-i', audio_path, '-c', 'copy', out_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Audio only! Just copy it so Streamlit can play it.
            print(f"Audio only (No video found) -> Copying: {clean_name}")
            shutil.copy2(audio_path, out_path)
            
    print("\nMedia pipeline complete! Streamlit is ready.")

if __name__ == "__main__":
    merge_media()