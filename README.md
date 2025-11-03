# 🎮🛰️ LLM-Powered Pokémon Data & Satellite Image Change Detection Tool

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**An interactive AI application combining RAG-powered Pokémon Q&A with satellite image change detection**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

This project is a comprehensive AI-powered tool that integrates:

1. **Pokémon Data Q&A System**: Uses Retrieval-Augmented Generation (RAG) to answer questions about a large Pokémon dataset
2. **Satellite Image Change Detection**: Analyzes and compares two images to detect changes over time
3. **Natural Language Interface**: Conversational AI that remembers context and provides intelligent responses

All components use **100% free, open-source software** with MIT or Apache 2.0 licenses, designed to run locally on Windows 11 with moderate hardware (16GB RAM or 8GB VRAM GPU).

### 🎨 Color Scheme
The UI features a beautiful **Gold, Purple, White, and Pink** color palette for a cohesive and modern look.

---

## ✨ Features

### 🎮 Pokémon Data Q&A (RAG)
- Load and query Pokémon datasets (CSV/Excel)
- Vector database powered by ChromaDB
- Semantic search across all Pokémon attributes
- Answer complex queries about types, stats, and characteristics

### 🛰️ Satellite Image Analysis
- **Image Captioning**: AI-generated descriptions of images using BLIP
- **Object Detection**: Identify objects/features using DETR
- **Change Detection**: Compare images using Structural Similarity Index (SSIM)
- **Detailed Reports**: Comprehensive analysis of differences between images

### 💬 Conversational AI
- Context-aware conversations using LangChain
- Multi-turn dialogue with memory
- Switch seamlessly between Pokémon queries and image analysis
- Natural language understanding

### 🎨 Modern UI
- Beautiful Gradio interface with custom color scheme
- Drag-and-drop file uploads
- Real-time chat interface
- Example queries to get started quickly

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                        │
│                  (Gradio - Gold/Purple/Pink Theme)            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    LangChain Agent                           │
│                  (Orchestration Layer)                       │
└─────┬─────────────────┬────────────────────┬────────────────┘
      │                 │                    │
┌─────▼─────┐  ┌────────▼─────────┐  ┌──────▼──────────┐
│  Pokemon  │  │  Image Caption   │  │  Image Compare  │
│  Database │  │     (BLIP)       │  │  (SSIM + DETR)  │
│   Tool    │  └──────────────────┘  └─────────────────┘
└─────┬─────┘
      │
┌─────▼──────────────────────────────────────────────────────┐
│              Vector Store (ChromaDB/FAISS)                  │
│         + Embeddings (SentenceTransformers)                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **LLM**: Databricks Dolly 2.0 (3B/7B) - Apache 2.0 licensed
2. **Embeddings**: all-MiniLM-L6-v2 - MIT licensed
3. **Image Captioning**: Salesforce BLIP - MIT licensed
4. **Object Detection**: Facebook DETR - Apache 2.0 licensed
5. **Vector DB**: ChromaDB/FAISS - Apache 2.0 licensed
6. **Orchestration**: LangChain - MIT licensed
7. **UI**: Gradio - Apache 2.0 licensed

---

## 📦 Installation

### Prerequisites

- **Python**: 3.10 or higher
- **OS**: Windows 11 (also works on Linux/macOS)
- **RAM**: 16GB recommended (8GB minimum with 3B model)
- **GPU**: Optional but recommended (8GB VRAM for 7B model, 4GB for 3B model)
- **VS Code**: Recommended IDE

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/CodexEterna.git
cd CodexEterna
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CUDA version if you have GPU)
# For CUDA 11.8:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CPU only:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install all other requirements
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import langchain, chromadb, transformers, cv2, gradio; print('✅ All packages installed successfully!')"
```

---

## 🚀 Usage

### Quick Start

1. **Activate your virtual environment** (if not already active):
   ```bash
   # Windows
   .\venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Open your browser** to `http://localhost:7860`

### Command Line Options

```bash
# Use lightweight simple agent (default, faster, less RAM)
python app.py

# Use full LLM agent (more advanced, requires more resources)
python app.py --full-llm

# Change port
python app.py --port 8080

# Create public share link
python app.py --share

# Combine options
python app.py --full-llm --port 8080
```

### Using the Application

#### 1️⃣ Pokémon Data Q&A

1. **Upload your Pokémon dataset** (CSV or Excel format)
   - A sample dataset is included in `data/pokemon/sample_pokemon.csv`
   - Format should include columns like: Name, Type1, Type2, HP, Attack, Defense, etc.

2. **Click "Load Pokémon Data"**

3. **Start asking questions**:
   - "What are the top 5 Pokémon with the highest Attack?"
   - "Tell me about Electric-type Pokémon"
   - "Which Water-type Pokémon have Defense over 100?"
   - "Compare Pikachu and Raichu"

#### 2️⃣ Satellite Image Analysis

1. **Upload two images**:
   - Image 1 (Before): Upload your first/earlier image
   - Image 2 (After): Upload your second/later image

2. **Ask about the images**:
   - "Describe the first image"
   - "What do you see in the second image?"
   - "Compare both images - what changed?"
   - "Are these the same location?"
   - "What are the major differences between the images?"

#### 3️⃣ Combined Usage

You can freely switch between topics in the same conversation:
```
You: "What is Pikachu's Attack stat?"
AI: "Pikachu has an Attack stat of 55..."

You: "Now describe the first image"
AI: "The first image shows a suburban area with..."

You: "Compare that to the second image"
AI: "Comparing the images, I notice several changes..."
```

---

## 📁 Project Structure

```
CodexEterna/
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/
│   ├── __init__.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── data_loader.py     # Pokémon data loading & RAG
│   │   ├── image_analyzer.py  # Image analysis (BLIP, DETR, SSIM)
│   │   └── llm_agent.py       # LangChain agent orchestration
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── gradio_app.py      # Gradio UI interface
│   │
│   └── utils/
│       └── __init__.py
│
├── data/
│   ├── pokemon/
│   │   └── sample_pokemon.csv # Sample Pokémon dataset
│   └── images/                # Uploaded images stored here
│
├── vectordb/                  # Vector database storage
└── logs/                      # Application logs
```

---

## 🔧 Configuration

Edit `config.py` to customize:

- **Models**: Change LLM, embedding, or vision models
- **Paths**: Modify data directories
- **Settings**: Adjust temperature, top_p, search parameters
- **UI**: Customize colors, port, etc.

### Using Different Models

**Smaller Model (Lower RAM usage)**:
```python
DEFAULT_LLM_MODEL = "databricks/dolly-v2-3b"  # ~6GB RAM
```

**Larger Model (Better performance)**:
```python
DEFAULT_LLM_MODEL = "databricks/dolly-v2-7b"  # ~14GB RAM
```

**Alternative Models** (all Apache 2.0/MIT):
- `tiiuae/falcon-7b-instruct`
- `mosaicml/mpt-7b-instruct`
- `meta-llama/Llama-2-7b-chat-hf` (requires approval)

---

## 💡 Tips & Tricks

### Performance Optimization

1. **Use 8-bit quantization** (enabled by default):
   - Reduces memory usage by ~50%
   - Minimal impact on quality

2. **Choose the right model**:
   - 3B model: Faster, uses less memory, good for most tasks
   - 7B model: Better understanding, more accurate, needs more resources

3. **GPU vs CPU**:
   - GPU: Much faster, especially for image processing
   - CPU: Works fine, just slower (5-10 seconds per response)

4. **Cache results**:
   - Image captions and object detection results are automatically cached
   - Vector store is persisted to disk (no re-embedding on restart)

### Troubleshooting

**Out of Memory Error**:
- Use the smaller 3B model instead of 7B
- Close other applications
- Run without `--full-llm` flag (uses simple agent)

**Slow responses**:
- First run downloads models (~5GB), subsequent runs are faster
- Use GPU if available
- Reduce `max_length` in config

**Import errors**:
```bash
pip install --upgrade -r requirements.txt
```

**Model download issues**:
- Check internet connection
- Models download from HuggingFace Hub automatically
- Clear cache: `rm -rf ~/.cache/huggingface/` (Linux) or delete `%USERPROFILE%\.cache\huggingface\` (Windows)

---

## 🧪 Testing

### Test Individual Components

**Test Data Loader**:
```bash
python -m src.modules.data_loader
```

**Test Image Analyzer**:
```bash
python -m src.modules.image_analyzer
```

**Test Simple Agent**:
```bash
python -m src.modules.llm_agent
```

### Sample Test Queries

**Pokémon Queries**:
- ✅ "List all Fire-type Pokémon"
- ✅ "Which Pokémon has the highest HP?"
- ✅ "Compare Bulbasaur and Charmander"
- ✅ "How many Legendary Pokémon are there?"

**Image Queries**:
- ✅ "What's in the first image?"
- ✅ "Describe both images"
- ✅ "What are the main differences?"
- ✅ "Has vegetation increased or decreased?"

---

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8GB (with 3B model, simple agent)
- **Storage**: 10GB free space
- **OS**: Windows 10+, Linux, macOS

### Recommended Requirements
- **CPU**: 8 cores
- **RAM**: 16GB
- **GPU**: 8GB VRAM (NVIDIA with CUDA)
- **Storage**: 20GB free space (for models and data)
- **OS**: Windows 11, Ubuntu 20.04+, macOS 11+

### Model Size Requirements

| Model | Parameters | RAM (8-bit) | RAM (16-bit) | GPU VRAM |
|-------|-----------|-------------|--------------|----------|
| Dolly 3B | 3 billion | ~6GB | ~12GB | 4GB |
| Dolly 7B | 7 billion | ~9GB | ~18GB | 8GB |
| BLIP | ~500M | ~2GB | ~4GB | 2GB |
| DETR | ~40M | ~1GB | ~2GB | 1GB |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style
- Follow PEP 8
- Add docstrings to functions
- Include type hints
- Write tests for new features

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

### Third-Party Licenses

All dependencies use permissive licenses:
- **Dolly 2.0**: Apache 2.0
- **BLIP**: MIT
- **DETR**: Apache 2.0
- **LangChain**: MIT
- **ChromaDB**: Apache 2.0
- **Gradio**: Apache 2.0

---

## 🙏 Acknowledgments

- **Databricks** for Dolly 2.0
- **Salesforce** for BLIP
- **Facebook/Meta** for DETR
- **LangChain** for the amazing orchestration framework
- **HuggingFace** for the Transformers library
- **Gradio** for the UI framework

---

## 📚 References

### Academic Papers
- [BLIP: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2201.12086)
- [DETR: End-to-End Object Detection with Transformers](https://arxiv.org/abs/2005.12872)
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

### Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers/)
- [Gradio Documentation](https://gradio.app/docs/)

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/Ethan-da-Tech-Wizard/CodexEterna/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Ethan-da-Tech-Wizard/CodexEterna/discussions)

---

## 🗺️ Roadmap

### Planned Features
- [ ] Support for more LLM models (Mistral, Llama 2, etc.)
- [ ] Advanced change detection algorithms
- [ ] Export analysis reports to PDF
- [ ] Batch image processing
- [ ] Custom dataset training
- [ ] REST API for programmatic access
- [ ] Mobile-friendly UI
- [ ] Multi-language support

### Completed Features
- [x] Pokémon RAG system
- [x] Image captioning and comparison
- [x] Conversational AI with memory
- [x] Beautiful custom UI
- [x] Comprehensive documentation

---

<div align="center">

**Built with ❤️ using Open-Source AI**

⭐ Star this repo if you find it useful! ⭐

</div>