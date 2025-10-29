from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import Client
from typing import Dict, List
import os, json

app = FastAPI()

client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
MODEL_NAME = os.getenv("OLLAMA_MODEL") or os.getenv("MIRANDA4_MODEL") or "mistral"

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

def hist_path(session_id: str) -> str:
    p = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(p, exist_ok=True)
    return os.path.join(p, "history.json")

def load_history(session_id: str) -> List[dict]:
    hp = hist_path(session_id)
    if os.path.exists(hp):
        try:
            with open(hp, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(session_id: str, history: List[dict]) -> None:
    with open(hist_path(session_id), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=0)

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Miranda4 — a focused, highly capable AI analyst for Ursa Space Systems. "
        "Be concise, accurate, and productive. Prioritize actionable insights, next steps, and clarity. "
        "Use Markdown when helpful. Maintain professional tone. "
        "You persist and recall session context. "
        "If the user mentions a number or target to remember, confirm and reuse it. "
        "If satellite images are uploaded, note filenames, time order if given, and provide a short plan for change detection."
    ),
}

@app.get("/health")
async def health() -> dict:
    try:
        _ = client.list()
        return {"ok": True, "model": MODEL_NAME}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama not reachable: {e}")

@app.get("/history")
async def get_history(session_id: str) -> dict:
    return {"history": load_history(session_id)}

@app.post("/reset")
async def reset_history(session_id: str) -> dict:
    save_history(session_id, [])
    return {"ok": True}

@app.post("/chat")
async def chat(req: ChatRequest) -> dict:
    try:
        history = load_history(req.session_id)
        history.append({"role": "user", "content": req.message})
        msgs = [SYSTEM_PROMPT] + history
        resp = client.chat(model=MODEL_NAME, messages=msgs, stream=False)
        content = resp.get("message", {}).get("content") if isinstance(resp, dict) else None
        if not content:
            raise RuntimeError(f"Unexpected Ollama response: {resp!r}")
        history.append({"role": "assistant", "content": content})
        save_history(req.session_id, history)
        return {"response": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

@app.post("/upload_image")
async def upload_image(session_id: str = Form(...), files: List[UploadFile] = File(...)) -> dict:
    try:
        sess_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(sess_dir, exist_ok=True)
        names = []
        for f in files:
            fp = os.path.join(sess_dir, f.filename)
            with open(fp, "wb") as out:
                out.write(await f.read())
            names.append(f.filename)

        history = load_history(session_id)
        note = f"Received {len(names)} image(s): " + ", ".join(names) + "."
        history.append({"role": "system", "content": note})
        save_history(session_id, history)

        return {"message": "Images cached.", "files": names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
