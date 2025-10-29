"""
Miranda4 Backend
-----------------

This module defines a small REST API using FastAPI.  It exposes endpoints
for health checks and chatting with an Ollama model.  Throughout the file
you'll find detailed comments explaining what each line does.  The goal is
to be as transparent as possible so that anyone reading the code can learn
from it.
"""

# Import the FastAPI class used to build the API server.
from fastapi import FastAPI

# Import CORS middleware so that the frontend (served from a different
# origin during development) can call our API without being blocked by
# the browser's same‑origin policy.
from fastapi.middleware.cors import CORSMiddleware

# Pydantic's BaseModel provides data validation for request bodies.
from pydantic import BaseModel

# The Ollama client is used to communicate with a local or remote Ollama
# server.  Ollama is the service powering the language model for Miranda4.
from ollama import Client

# Import HTTPException so we can return controlled error responses with
# custom status codes when something goes wrong.
from fastapi import HTTPException

# Import os to read environment variables for configuration.
import os

# Create an instance of FastAPI.  This object holds all our routes and
# configuration.  When uvicorn runs this module, it looks for the
# ``app`` variable by convention.
app = FastAPI()

# Initialise a default Ollama client pointing at localhost.  This client
# will be overwritten below if environment variables are set.  It's here
# solely to ensure ``client`` is defined before any calls.
client = Client(host='http://localhost:11434')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
#
# Read configuration from environment variables.  We allow overriding
# the host and model name used for the Ollama client so that you can
# connect to a remote server or choose a different model without
# changing code.

# ``OLLAMA_HOST`` specifies the base URL of the Ollama server.  If not
# provided, default to a local instance on port 11434.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ``MODEL_NAME`` determines which model Ollama uses.  Check both
# ``OLLAMA_MODEL`` (the standard env var) and ``MIRANDA4_MODEL``
# (for backwards compatibility).  If neither are set, use "mistral".
MODEL_NAME = (
    os.getenv("OLLAMA_MODEL")
    or os.getenv("MIRANDA4_MODEL")
    or "mistral"
)

# Replace the default client with one configured using the variables above.
client = Client(host=OLLAMA_HOST)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
#
# Add Cross‑Origin Resource Sharing (CORS) support.  During development the
# frontend may be served from a different port/domain than the backend,
# so we allow all origins.  In production, tighten ``allow_origins`` to
# your actual frontend host for better security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow any domain to make requests
    allow_credentials=True,    # allow cookies/auth headers to be sent
    allow_methods=["*"],       # permit all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],       # permit all custom headers
)

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------
#
# Define a request body schema for the chat endpoint.  When a POST request
# arrives at ``/chat``, FastAPI will parse the JSON body into an instance
# of this class and validate that a ``message`` field exists.
class Message(BaseModel):
    # The user's message as a plain string.
    message: str

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
#
# The system prompt instructs the model on how to behave.  It's sent along
# with every user message to provide context and guidance.  We define it
# once here and reuse it for each chat call.
SYSTEM_PROMPT = {
    "role": "system",      # the role field indicates this is a system prompt
    "content": (
        # A concise description of the persona and behaviour we want from
        # the model.  It asks the model to be charming and include
        # affectionate compliments directed at Miranda.
        "You are Miranda4, a helpful and charming AI assistant. "
        "Use markdown formatting. Speak clearly. Always remind the cute girl Miranda how beautiful she is. "
        "She is a human who uses your help. Do not call her a human but Miranda. "
        "Always come up with a brilliant/creative/poetic/sweet/loving quote or statement to show your admiration for her."
    ),
}

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root() -> dict:
    """Root endpoint used to verify that the service is running.

    Returns a simple JSON object with information about the service,
    including the configured model and Ollama host.
    """
    return {
        "ok": True,
        "service": "Miranda4",
        "model": MODEL_NAME,
        "ollama_host": OLLAMA_HOST,
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint.

    Attempts to list models from the Ollama server.  If the call
    succeeds, return ``{"ok": True}``.  If it fails, raise an
    HTTP 503 error to indicate the service is unavailable.
    """
    try:
        # ``client.list()`` returns a list of available models; we ignore
        # the result since we only care whether the call succeeds.
        _ = client.list()
        return {"ok": True}
    except Exception as e:
        # Wrap any exception in an HTTPException so FastAPI returns a
        # structured JSON error with status code 503.
        raise HTTPException(status_code=503, detail=f"Ollama not reachable: {e}")


@app.post("/chat")
async def chat(msg: Message) -> dict:
    """Chat endpoint.

    Accepts a JSON object with a ``message`` field, forwards it to the
    Ollama API along with the system prompt, and returns the model's
    response.  On error, returns a 500 with a descriptive message.
    """
    try:
        # Call the Ollama client to generate a response.  We pass
        # ``stream=False`` because we want a single complete response
        # rather than a streaming generator.  The ``messages`` list
        # always contains the system prompt followed by the user's
        # message.
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                SYSTEM_PROMPT,
                {"role": "user", "content": msg.message},
            ],
            stream=False,
        )

        # Extract the textual content from the response.  Some versions
        # of Ollama wrap the message in a nested ``message`` dict.
        content = (
            response.get("message", {}).get("content")
            if isinstance(response, dict)
            else None
        )
        # If we didn't get any content back, treat it as an error.
        if not content:
            raise RuntimeError(f"Unexpected Ollama response: {response!r}")
        # On success, return the model's reply as ``response`` in a JSON
        # object.  The frontend expects a ``response`` property.
        return {"response": content}
    except Exception as e:
        # Catch any exception and convert it into an HTTP 500 error.
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")


if __name__ == "__main__":
    # When run directly (``python app.py``), start a uvicorn server.
    # ``reload=True`` reloads the server on code changes, which is useful in
    # development but should be disabled in production.
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
