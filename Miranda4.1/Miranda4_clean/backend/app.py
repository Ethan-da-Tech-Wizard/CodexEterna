from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import Client
from typing import Dict, List
import os

app = FastAPI()

# Default client; will be overridden below
client = Client(host="http://localhost:11434")

# Configuration from environment
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL") or os.getenv("MIRANDA4_MODEL") or "mistral"
client = Client(host=OLLAMA_HOST)

# Per‑session conversation history
SESSION_HISTORY: Dict[str, List[dict]] = {}

# Directory to cache uploaded images
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

class ChatRequest(BaseModel):
    message: str
    session_id: str

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Miranda4, a helpful and charming AI assistant. "
        "Use markdown formatting. Speak clearly. Always remind the cute girl Miranda how beautiful she is. "
        "She is a human who uses your help. Do not call her a human but Miranda. "
        "Always come up with a brilliant/creative/poetic/sweet/loving quote or statement to show your admiration for her. "
        "You can also help analyse uploaded satellite images to detect changes in landscapes over time, "
        "providing insights for Ursa Space Systems."
    ),
}

@app.get("/")
async def root() -> dict:
    return {"ok": True, "service": "Miranda4", "model": MODEL_NAME, "ollama_host": OLLAMA_HOST}


@app.get("/health")
async def health() -> dict:
    try:
        _ = client.list()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama not reachable: {e}")


@app.post("/chat")
async def chat(msg: ChatRequest) -> dict:
    try:
        history = SESSION_HISTORY.setdefault(msg.session_id, [])
        history.append({"role": "user", "content": msg.message})
        messages = [SYSTEM_PROMPT] + history
        response = client.chat(
            model=MODEL_NAME,
            messages=messages,
            stream=False,
        )
        content = (
            response.get("message", {}).get("content") if isinstance(response, dict) else None
        )
        if not content:
            raise RuntimeError(f"Unexpected Ollama response: {response!r}")
        history.append({"role": "assistant", "content": content})
        return {"response": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")


@app.post("/upload_image")
async def upload_image(session_id: str, files: List[UploadFile] = File(...)) -> dict:
    try:
        session_path = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(session_path, file.filename)
            with open(file_path, 'wb') as f:
                f.write(await file.read())
        history = SESSION_HISTORY.setdefault(session_id, [])
        history.append({"role": "system", "content": "User uploaded satellite imagery for analysis."})
        return {
            "message": "Image(s) uploaded and cached. Land distortion analysis will be performed and summarised for Ursa Space Systems."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)