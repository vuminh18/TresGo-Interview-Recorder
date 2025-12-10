import os
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime
import pytz

# ==============================
# PATH CONFIGURATION
# ==============================
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# ==============================
# TIMEZONE CONFIGURATION
# ==============================
try:
    # Set timezone to Vietnam (Asia/Bangkok)
    VN_TZ = pytz.timezone('Asia/Bangkok')
except:
    # Fallback to local system timezone if pytz fails
    VN_TZ = datetime.now().astimezone().tzinfo

# ==============================
# VALID TOKENS LIST
# ==============================
VALID_TOKENS = {
    "DEV_TEAM_KEY_2025": "Administrator",
    "TEACHER_KEY": "Tran Hung",
    "11247188": "Nguyen Thi Thuy Linh",
    "11247205": "Vu Kim Minh",
    "11247218": "Pham Mai Phuong",
    "user_guest": "Guest User 1"
}

# ==============================
# Pydantic DATA MODELS
# ==============================
class TokenCheck(BaseModel):
    token: str

class SessionStart(BaseModel):
    token: str
    userName: str

class SessionFinish(BaseModel):
    token: str
    folder: str
    questionsCount: int

# ==============================
# UPLOAD CONFIGURATION (NEW)
# ==============================
# 1. File size limit (e.g., 50MB = 50 * 1024 * 1024 bytes)
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# 2. Allowed file extensions (Video only)
ALLOWED_EXTENSIONS = {".webm", ".mp4", ".mov", ".mkv"}