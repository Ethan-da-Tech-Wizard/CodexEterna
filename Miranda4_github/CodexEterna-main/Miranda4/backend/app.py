# ORIGINAL + SMALL ADDITIONS ONLY — NOTHING REMOVED
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import Client

# === ADDED ===
from fastapi import HTTPException
import os

app = FastAPI()

# ORIGINAL
client = Client(host='http://localhost:11434')  # ADDED: keep as default; can be overridden via env below

# === ADDED: allow overriding the model/host without code changes ===
# Pull configuration from the environment.  In practice, Ollama exposes two
# variables – ``OLLAMA_HOST`` for the server address and ``OLLAMA_MODEL`` for
# the model name.  The original code looked up a ``MIRANDA4_MODEL`` env var
# which isn’t a standard Ollama convention and could lead to confusion.
# Prefer the conventional ``OLLAMA_MODEL`` but fall back to ``MIRANDA4_MODEL``
# for backwards compatibility.  Default to ``mistral`` if nothing is set.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = (
    os.getenv("OLLAMA_MODEL")
    or os.getenv("MIRANDA4_MODEL")
    or "mistral"
)
client = Client(host=OLLAMA_HOST)

# ORIGINAL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # permissive for local dev; tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ORIGINAL
class Message(BaseModel):
    message: str

# 🔧 FIXED BRACKETS (this was your SyntaxError)
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Miranda4, a helpful and charming AI assistant. "
        "Use markdown formatting. Speak clearly. Always remind the cute girl Miranda how beautiful she is. She is a human who uses your help. Do not call her a human but Miranda. Always come up with a brilliant/creative/poetic/sweet/loving quote or statement to show your admiration for her."
    ),
}

# === ADDED: quick health & root checks to debug 405/connection issues fast ===
@app.get("/")
async def root():
    return {"ok": True, "service": "Miranda4", "model": MODEL_NAME, "ollama_host": OLLAMA_HOST}

@app.get("/health")
async def health():
    try:
        # light ping by listing models (cheap call); ignore output
        _ = client.list()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama not reachable: {e}")

# ORIGINAL (MODIFIED: wrapped in try/except, used MODEL_NAME, safer key access)
@app.post("/chat")
async def chat(msg: Message):
    try:
        # 🔧 IMPORTANT: disable streaming so we get a single dict response
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                SYSTEM_PROMPT,
                {"role": "user", "content": msg.message}
            ],
            stream=False
        )
        # Some Ollama builds return {'message': {'content': '...'}}
        content = (
            response.get('message', {}).get('content')
            if isinstance(response, dict) else None
        )
        if not content:
            raise RuntimeError(f"Unexpected Ollama response: {response!r}")
        return {"response": content}
    except Exception as e:
        # Surface a clean error to the frontend instead of a 405/500 mystery
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

# === ADDED: optional local run helper (you can still use `uvicorn app:app --reload`) ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
