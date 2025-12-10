import os
import re
import json
import whisper
from datetime import datetime
from config import VN_TZ  # Import timezone from config

# ==============================
# LOAD WHISPER AI MODEL
# ==============================
# This runs once when the server starts
print("--- LOADING AI MODEL (WHISPER)... PLEASE WAIT ---")
try:
    # Using 'base' model for balance between speed and accuracy on CPU
    stt_model = whisper.load_model("base")
    print("--- MODEL LOADED SUCCESSFULLY! ---")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    stt_model = None

# ==============================
# HELPER FUNCTIONS
# ==============================

def generate_folder_name(user_name: str) -> str:
    """Generate a safe folder name with timestamp: DD_MM_YYYY_HH_mm_user_name"""
    now = datetime.now(VN_TZ)
    time_str = now.strftime("%d_%m_%Y_%H_%M")
    # Sanitize username (remove special characters)
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_name)
    return f"{time_str}_{safe_name}"

def update_metadata(folder_path, data: dict):
    """Safely update or create the meta.json file"""
    meta_path = folder_path / "meta.json"
    current_meta = {}
    
    # Read existing data if file exists
    if meta_path.exists():
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                current_meta = json.load(f)
        except:
            pass
            
    # Update with new data
    current_meta.update(data)
    
    # Write back to file
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(current_meta, f, ensure_ascii=False, indent=2)

def run_stt_task(video_path: str, folder_path, question_index: int):
    """
    Background Task: Transcribe video audio to text using OpenAI Whisper.
    Designed to be robust and handle mixed languages (Vietnamese/English).
    """
    if stt_model is None:
        return

    try:
        # 1. Check for empty/corrupted video files
        if os.path.getsize(video_path) < 1000: 
            print(f"--> [Skip] Q{question_index}: Video file too small or empty.")
            return

        print(f"--> Processing STT for Q{question_index} (Optimized Prompt)...")

        # 2. Transcription Configuration
        result = stt_model.transcribe(
            str(video_path), 
            fp16=False, # Must be False for CPU execution
            
            # --- PROMPT ENGINEERING ---
            # Providing context and keywords to improve accuracy
            initial_prompt=(
                "Interview context. The candidate answers in English. "
                "Keywords:  IT, programming, "
                "teamwork, development, project."
            ),
            
            # --- TUNING PARAMETERS ---
            condition_on_previous_text=False, # Prevent repetition loops
            temperature=0.0,      # =0 means deterministic (most probable) output
            beam_size=2,          # =2 means slightly deeper search for better accuracy
            patience=1.0,         
        )
        
        text_content = result["text"].strip()
        
        # Debug Log
        print(f"   + RAW OUTPUT: '{text_content}'")

        # 3. Filter Hallucinations (Common Whisper issue with silence)
        bad_phrases = ["Subtitles by", "Amara.org", "Thank you", "Watching"]
        if not text_content or any(phrase in text_content for phrase in bad_phrases):
             if len(text_content) < 5: 
                 text_content = "[Audio unclear / No speech detected]"

        # 4. Save to transcript.txt
        transcript_path = folder_path / "transcript.txt"
        timestamp = datetime.now(VN_TZ).strftime("%H:%M:%S")
        log_line = f"[{timestamp}] Question {question_index}:\n{text_content}\n{'-'*30}\n"

        with open(transcript_path, "a", encoding="utf-8") as f:
            f.write(log_line)

        print(f"--> Finished Q{question_index}")

    except Exception as e:
        print(f"STT Error for Q{question_index}: {e}")