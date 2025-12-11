# TresGo - Video Interview Platform

**TresGo** is a simple online video interview platform that allows candidates to record video responses to questions and automatically upload them to the server in real time.

![Demo Screenshot](./static/img/screenshot_demo.png) 

## 1. System Architecture & Workflow

### 1.1. Architecture

The system follows a traditional **Client–Server** architecture.

* **Client (Frontend):** Built with HTML, CSS, and Vanilla JS. Handles sequential UI flow, camera/microphone access (`getUserMedia`), video recording (`MediaRecorder`), and upload/retry logic.
* **Server (Backend):** Provides REST API endpoints, handles token authentication, manages session state, and stores video files in a predefined folder structure.

### 1.2. Sequential Workflow

The workflow is **sequential** and strictly dependent on the results of API calls.

1. **Login (`login.js`):**
   * Enter **Token** and **Name**.
   * Call **`/api/verify-token`**.
   * Call **`/api/session/start`** → Store **`userToken`** and **`sessionFolder`** in `localStorage`.
   * Redirect to `interview.html`.

2. **Recording (Q1–Q5):**
   * Request Camera/Mic access (`getUserMedia`).
   * **`MediaRecorder`** starts recording the current question.

3. **Upload (Per Question):**
   * Click **Next Question** → Stop recording → Trigger upload logic.
   * Client calls **`/api/upload-one`** (multipart/form-data).
   * **Blocking:** The client only moves to the next question after receiving a **200 OK** response from the server.

4. **Finish:** After Q5, click **Finish Interview** → Call **`/api/session/finish`**.

---

## 2. Frontend Technologies & Structure

### 2.1. Core Technologies

* **HTML5/CSS3:** Interface layout (`login.html`, `interview.html`, `*.style.css`).
* **Vanilla JavaScript:** Handles all complex client-side logic.
    * `MediaDevices.getUserMedia`: Camera & microphone access.
    * `MediaRecorder`: Record video into a Blob.
    * `localStorage`: Maintain session state (`userToken`, `sessionFolder`).

### 2.2. API Contract (Client Perspective)

All API calls use POST.

| Endpoint | Purpose | Fields | Notes |
| --- | --- | --- | --- |
| `/api/verify-token` | Token validation | `token` | Must succeed before `/session/start`. |
| `/api/session/start` | Initialize interview session | `token`, `userName` | Returns `folder` saved to `localStorage`. |
| `/api/upload-one` | Upload video per question | `token`, `folder`, `questionIndex`, `video` | Multipart; retry logic applies. |
| `/api/session/finish` | Finalize session | `token`, `folder`, `questionsCount` | Ends session. |

---

## 3. Reliability & Retry Mechanism

To handle network issues, the Frontend implements Retry with Exponential Backoff.

### 3.1. Retry Policy

* Applies to: Network errors, fetch errors, and server errors (HTTP ≥ 500).
* Automatic retries: Up to **3 attempts**.
* Exponential Backoff: Wait time increases (2¹s, 2²s, 2³s).

### 3.2. Error Handling & UI

* Prevent next question if retry fails 3 times.
* Manual **Retry** button available.
* Status indicators: `Requesting permissions`, `Recording`, `Uploading`, `Upload Success`, `Retrying in X s`, `Upload Failed`.

---

## 4. System Requirements

* **HTTPS** is required for camera/mic permission, external access (handled by Ngrok).
* **File Size:** Max 50MB per question.
* **Retry Policy:** 3 Automatic attempts (Exponential backoff: 2s, 4s, 8s) + Manual Retry button.
* **Server Storage:** The folder structure on the server must follow the rule:  
  `{DD_MM_YYYY_HH_mm_user_name/}`
  * (Example: `03_12_2025_13_39_candidate_nguyen_van_a/`)
  * Mandatory timezone: **Asia/Bangkok**.

---

## Key Features

* **Sequential Recording:** Interview questions are recorded in order (Question 1 → Question 2 → ...).
* **Real-time Upload:** The video is uploaded immediately after each question ends (preventing data loss).
* **Auto-Naming:** The system automatically organizes storage folders based on candidate name and timestamp (`DD_MM_YYYY...`).
* **Speech-to-Text (Bonus):** Integrated OpenAI Whisper to automatically generate transcripts from videos.
* **Token Authentication:** Candidate authentication using an assigned token.

---

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn.
* **Frontend:** Vanilla JS, HTML5, CSS3 (Fetch API, MediaRecorder API).
* **Utilities:** FFmpeg, OpenAI Whisper (AI).


## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/vuminh18/TresGo-Interview-Recorder.git](https://github.com/vuminh18/TresGo-Interview-Recorder.git)
    cd TresGo-Interview-Recorder/backend
    ```

2.  **Install dependencies:**
    ```bash
    pip install fastapi uvicorn python-multipart pytz openai-whisper
    ```
    *(Note: You need to download ffmpeg.exe and place it in the root directory of the project.)*

3.  **Running Server:**
    ### Method 1: Localhost (Offline Testing)
    Use this for development or testing on the same machine.
    1.  Open terminal in `backend/` folder.
    2.  Run server:
        ```bash
        python main.py
        ```
    3.  Access: `http://127.0.0.1:8002`
        ```bash
        python main.py
        ```
    ### Method 2: Public Access via Ngrok (HTTPS - Recommended)
    **Required for accessing Camera/Mic from other devices.**

    1.  Start the Python Server (Method 1).
    2.  Open a **new terminal** in `backend/` and run:
        ```powershell
        .\ngrok http --domain=primulaceous-unsluggishly-ashton.ngrok-free.dev 8002
        ```
    3.  Copy the `https://...` link and open it in your browser.

## Authentication Credentials

To access the system, please use one of the following **Valid Token & Name pairs**.
*(Note: The system enforces strict validation. The "Name" must match the "Token" exactly).*

| Role | Token | Required Name |
| :--- | :--- | :--- |
| **Administrator** | `DEV_TEAM_KEY_2025` | `Administrator` |
| **Lecturer** | `TEACHER_KEY` | `Tran Hung` |
| **Student 1** | `11247188` | `Nguyen Thi Thuy Linh` |
| **Student 2** | `11247205` | `Vu Kim Minh` |
| **Student 3** | `11247218` | `Pham Mai Phuong` |
| **Guest** | `user_guest` | `Guest User 1` |

*(Tip: Copy and paste the Name to avoid typos).*
## Development team
This project was developed by the 3-member team TresGo:
* Nguyen Thi Thuy Linh
* Vu Kim Minh
* Pham Mai Phuong

*Project for Computer Networking Course - 2025*
