"""
Configuration settings for the application.
"""

import os

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
POKEMON_DATA_DIR = os.path.join(DATA_DIR, "pokemon")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
VECTORDB_DIR = os.path.join(PROJECT_ROOT, "vectordb")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Model Settings
DEFAULT_LLM_MODEL = "databricks/dolly-v2-3b"  # Smaller model by default
FULL_LLM_MODEL = "databricks/dolly-v2-7b"     # Larger, more capable model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CAPTIONING_MODEL = "Salesforce/blip-image-captioning-base"
DETECTION_MODEL = "facebook/detr-resnet-50"

# LLM Settings
USE_8BIT_QUANTIZATION = True  # Reduces memory usage
MAX_SEQUENCE_LENGTH = 512
TEMPERATURE = 0.7
TOP_P = 0.95
REPETITION_PENALTY = 1.15

# RAG Settings
VECTOR_SEARCH_K = 5  # Number of documents to retrieve
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Image Analysis Settings
OBJECT_DETECTION_THRESHOLD = 0.7  # Confidence threshold for object detection
MIN_CHANGE_AREA = 100  # Minimum area (pixels) to consider as a change

# UI Settings
GRADIO_SERVER_PORT = 7860
GRADIO_SERVER_NAME = "0.0.0.0"
SHARE_PUBLIC_LINK = False

# Color Scheme (Gold, Purple, White, Pink)
COLORS = {
    "primary": "#9370DB",      # Medium Purple
    "secondary": "#DAA520",    # Goldenrod
    "accent": "#FFB6C1",       # Light Pink
    "background": "#FFFFFF",   # White
    "light_bg": "#F8F0FF"      # Very light purple
}

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Sample Data
SAMPLE_POKEMON_FILE = os.path.join(POKEMON_DATA_DIR, "sample_pokemon.csv")

# Create directories if they don't exist
for directory in [DATA_DIR, POKEMON_DATA_DIR, IMAGES_DIR, VECTORDB_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)
