# main.py
print("---- SERVER IS STARTING, PLEASE WAIT... ----")

import shutil
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- IMPORT MODULES ---
from config import (
    UPLOAD_DIR, STATIC_DIR, VN_TZ, VALID_TOKENS, 
    TokenCheck, SessionStart, SessionFinish,
    MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS 
)
from utils import generate_folder_name, update_metadata, run_stt_task

# ==============================
# APP INITIALIZATION
# ==============================
app = FastAPI(title="TRESGO - Interview Platform", version="1.0")

# Configure CORS (Allow all origins for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (Frontend)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==============================
# API ROUTES
# ==============================

@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the main HTML page"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Error: index.html not found in static folder</h1>")

@app.post("/api/verify-token")
async def verify_token(data: TokenCheck):
    """Endpoint to validate user token"""
    if data.token in VALID_TOKENS:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Invalid Token")

@app.post("/api/session/start")
async def start_session(data: SessionStart):
    """
    Start session: Validates Token AND matches Name.
    Creates storage folder if valid.
    """
    # 1. Check if token exists
    if data.token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Token not found.")

    # 2. STRICT NAME VALIDATION [NEW]
    # Get the real name associated with this token
    expected_name = VALID_TOKENS[data.token]
    
    input_name_norm = data.userName.strip().lower()
    expected_name_norm = expected_name.strip().lower()

    if input_name_norm != expected_name_norm:
        raise HTTPException(
            status_code=401, 
            detail=f"Name mismatch! This token belongs to: {expected_name}"
        )
  
    # 3. Create Folder
    folder_name = generate_folder_name(data.userName)
    session_path = UPLOAD_DIR / folder_name
    session_path.mkdir(parents=True, exist_ok=True)

    # 4. Save Initial Metadata
    init_meta = {
        "userName": data.userName,
        "tokenOwner": expected_name, # Record the official name
        "startTime": datetime.now(VN_TZ).isoformat(),
        "status": "started",
        "files": []
    }
    update_metadata(session_path, init_meta)

    return {"ok": True, "folder": folder_name}

@app.post("/api/upload-one")
async def upload_one(
    background_tasks: BackgroundTasks,
    token: str = Form(...),
    folder: str = Form(...),
    questionIndex: int = Form(...),
    video: UploadFile = File(...)
):
    """
    Endpoint to receive video file for each question.
    It saves the file and triggers the background STT task.
    """
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid Token")

    session_path = UPLOAD_DIR / folder
    if not session_path.exists():
        raise HTTPException(status_code=404, detail="Session folder not found")

    # Validate file extension
    file_ext = Path(video.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format! Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    # Save video file & check size limit (chunk reading)
    file_name = f"Q{questionIndex}.webm"
    dest = session_path / file_name

    try:
        real_file_size = 0
        with dest.open("wb") as buffer:
            while True:
                # Read in chunks (1MB = 1024*1024 bytes)
                chunk = await video.read(1024 * 1024) 
                if not chunk:
                    break
                
                real_file_size += len(chunk)
                
                # Check limit
                if real_file_size > MAX_FILE_SIZE_BYTES:
                    buffer.close()
                    dest.unlink() # Delete incomplete file
                    limit_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
                    raise HTTPException(
                        status_code=413, 
                        detail=f"File too large! Limit is {limit_mb}MB."
                    )
                
                buffer.write(chunk)
                
    except HTTPException as he:
        raise he # Re-raise HTTP exceptions (like 413)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File write error: {str(e)}")

    # Update Metadata
    meta_path = session_path / "meta.json"
    if meta_path.exists():
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        if "files" not in meta: meta["files"] = []
        
        meta["files"].append({
            "questionIndex": questionIndex,
            "fileName": file_name,
            "fileSize": f"{round(real_file_size / 1024, 2)} KB",
            "uploadedAt": datetime.now(VN_TZ).isoformat()
        })
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    # 5. Trigger Background STT
    background_tasks.add_task(run_stt_task, str(dest), session_path, questionIndex)

    return JSONResponse({"ok": True, "savedAs": file_name})

@app.post("/api/session/finish")
async def finish_session(data: SessionFinish):
    """Endpoint to finalize the session"""
    session_path = UPLOAD_DIR / data.folder
    update_metadata(session_path, {
        "status": "finished",
        "totalQuestions": data.questionsCount,
        "endTime": datetime.now(VN_TZ).isoformat()
    })
    return {"ok": True}

# ==============================
# SERVER ENTRY POINT
# ==============================
if __name__ == "__main__":
    import uvicorn
    print("=====================================================")
    print("   SERVER TRESGO IS RUNNING ON PORT 8002... ")
    print("   PLEASE ACCESS: http://127.0.0.1:8002")
    print("=====================================================")
    
    # Run uvicorn server (reload=False to prevent Windows process errors)
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)