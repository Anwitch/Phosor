# Phosor 🧠📸

**Photo Sorting Orchestrator for Faces**

Automated face-based photo clustering and organization system powered by **UniFace** – the state-of-the-art face detection and recognition model.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🎯 Overview

Phosor automatically groups photos by detected faces using cutting-edge facial recognition technology. It scans a folder of photos, detects faces with **UniFace**, generates embeddings, performs intelligent clustering, and organizes photos into per-person folders.

**Perfect For:**
- 📷 Event photographers (weddings, graduations, conferences)
- 🏢 Documentation teams managing large photo collections
- 👥 Anyone organizing photos with multiple people
- 🎨 Content creators managing portrait galleries

---

## ✨ Key Features

### 🔍 Smart Face Detection
- **Powered by UniFace** – Industry-leading face detection and recognition
- 512-dimensional face embeddings for high accuracy
- Batch processing with progress tracking
- Handles multiple faces per image

### 🎯 Intelligent Clustering
- **DBSCAN algorithm** with cosine distance metrics
- Automatically groups similar faces together
- Configurable clustering parameters (eps, min_samples)
- Minimum faces per cluster filtering to avoid false positives

### 📊 Interactive Web Dashboard
- **Modern UI** with Alpine.js and Tailwind CSS
- Real-time cluster management (create, rename, merge, delete)
- Image gallery with lightbox viewer
- Drag-and-drop unclustered images to clusters
- Alphabetically sorted cluster grid
- 24-hour browser caching for blazing-fast performance

### 🚀 CLI Pipeline
- Command-line interface for batch processing
- Recursive directory scanning
- Copy or move files to organized folders
- JSON metadata export (embeddings, summaries)
- Dry-run mode to preview results

### 🔒 Privacy-First
- **100% local processing** – All data stays on your device
- No cloud uploads or external API calls
- Complete control over your photos

---

## 🛠️ Technology Stack

### Backend
- **Python 3.10+** – Modern async/await support
- **FastAPI 0.123.0** – High-performance web framework
- **UniFace** – Face detection and embedding generation
- **scikit-learn** – DBSCAN clustering algorithm
- **Uvicorn** – Lightning-fast ASGI server

### Frontend
- **Alpine.js 3.x** – Lightweight reactive framework
- **Tailwind CSS 3.4.1** – Utility-first CSS
- **Server-side rendering** with Jinja2 templates

### Face Recognition
- **UniFace** – State-of-the-art face detection model
  - RetinaFace for face detection
  - ArcFace for face recognition
  - 512-dimensional embedding vectors
  - Robust to pose, lighting, and occlusion variations

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Anwitch/Phosor.git
cd Phosor
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

This will install all required packages including:
- `uniface` – Face detection and recognition
- `fastapi` – Web framework
- `scikit-learn` – Clustering algorithms
- `opencv-python` – Image processing
- And more...

---

## 🚀 Quick Start

### Step 1: Prepare Your Photos
Place photos in the `data/input/` folder:
```bash
mkdir -p data/input
cp /path/to/your/photos/*.jpg data/input/
```

### Step 2: Run the CLI Pipeline
```bash
phosor scan --input data/input --output data/output
```

This will:
1. 🔍 Scan all images in `data/input/`
2. 🧠 Detect faces using **UniFace**
3. 📊 Generate 512-dim embeddings
4. 🎯 Cluster similar faces with DBSCAN
5. 📁 Organize photos into `data/output/Person_01/`, `Person_02/`, etc.

### Step 3: Launch Web Dashboard
```bash
phosor serve
```

Open http://127.0.0.1:8000 in your browser to:
- View all clusters and statistics
- Rename clusters (e.g., "Person_01" → "John Smith")
- Merge similar clusters
- Move unclustered images to correct clusters
- Delete unwanted images

---

## 📖 Usage Examples

### Basic Scan with Config File
```bash
phosor scan --config configs/config.toml
```

### Dry Run (Preview Only)
```bash
phosor scan --input data/input --output data/output --dry-run
```

### View Clustering Summary
```bash
phosor summary data/output/clusters_summary.json
```

### Start Dashboard on Custom Port
```bash
phosor serve --host 0.0.0.0 --port 5000 --reload
```

---

## ⚙️ Configuration

Create a `config.toml` file (see `configs/config.example.toml`):

```toml
[input]
dir = "data/input"          # Input photo directory
recursive = true            # Scan subdirectories
min_file_size_kb = 50      # Skip tiny files

[output]
dir = "data/output"         # Output directory
mode = "copy"               # "copy" or "move"

[clustering]
method = "dbscan"           # Clustering algorithm
eps = 0.5                   # Max distance for same cluster
min_samples = 3             # Min faces to form cluster
min_faces_per_cluster = 3   # Filter small clusters

[representative]
mode = "crop"               # "crop", "bbox", or "annotated"
thumbnail_size = 200        # Thumbnail dimensions

[logging]
level = "INFO"
file = "logs/phosor.log"
```

### Key Parameters Explained

- **eps (0.3-0.7)**: Lower = stricter clustering (fewer false positives)
- **min_samples (2-5)**: Higher = larger clusters only
- **min_faces_per_cluster (3-10)**: Filter out clusters with too few faces

---

## 📂 Output Structure

After running `phosor scan`, your output directory will look like:

```
data/output/
├── Person_01/              # Cluster 1
│   ├── photo1.jpg
│   ├── photo5.jpg
│   └── photo12.jpg
├── Person_02/              # Cluster 2
│   ├── photo3.jpg
│   └── photo8.jpg
├── unclustered/            # Unmatched faces
│   └── photo15.jpg
├── representative/         # Cluster thumbnails
│   ├── Person_01.jpg
│   └── Person_02.jpg
├── embeddings.json         # Face embeddings
└── clusters_summary.json   # Statistics
```

---

## 🧪 Testing

Phosor has **19/19 tests passing** with comprehensive coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Real-world test results:
# ✅ 78 images processed
# ✅ 400 faces detected
# ✅ 20 clusters created
```

---

## 🏗️ Project Structure

```
Phosor/
├── src/
│   ├── core/                    # CLI pipeline
│   │   ├── cli.py              # Typer commands
│   │   ├── face_engine.py      # UniFace wrapper
│   │   ├── clustering.py       # DBSCAN clustering
│   │   ├── file_scanner.py     # Image discovery
│   │   ├── folder_manager.py   # Output operations
│   │   └── ...
│   └── frontend/               # Web dashboard
│       ├── app.py              # FastAPI application
│       ├── api/
│       │   ├── clusters.py     # Cluster management
│       │   └── images.py       # Image serving
│       └── templates/
│           ├── index.html      # Dashboard
│           └── cluster_detail.html
├── configs/
│   └── config.toml             # Configuration
├── tests/                       # Unit tests
├── data/
│   ├── input/                  # Input photos
│   └── output/                 # Organized results
└── pyproject.toml              # Dependencies
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📋 Roadmap

- [x] **Phase 1-11: Core Features** ✅
  - CLI pipeline with UniFace integration
  - DBSCAN clustering
  - Web dashboard with full CRUD operations
  - Image caching and performance optimization
  
- [ ] **Phase 12: Advanced Features**
  - Incremental updates with hash tracking
  - SQLite metadata storage
  - Batch operations UI
  - Export/import functionality

- [ ] **Phase 13: Enterprise Features**
  - User authentication
  - Multi-user support
  - Cloud storage integration
  - Advanced analytics

---

## 🐛 Known Issues & Fixes

See [DEVLOG.md](DEVLOG.md) for detailed bug history and resolutions.

---

## 📄 Documentation

- **[PHOSOR_SPEC.md](PHOSOR_SPEC.md)** – Technical specification and API documentation
- **[AGENT_STEPS.md](AGENT_STEPS.md)** – Development guidelines for AI agents
- **[DEVLOG.md](DEVLOG.md)** – Bug history and fixes
- **[Agent_Guide.md](Agent_Guide.md)** – Documentation index

---

## 🙏 Credits

- **UniFace** – Face detection and recognition engine
- **FastAPI** – Modern web framework
- **scikit-learn** – Machine learning algorithms
- **Alpine.js** – Lightweight reactive framework
- **Tailwind CSS** – Utility-first CSS framework

---

## 📧 Support

For issues, questions, or feature requests:
- 🐛 Open a [GitHub Issue](https://github.com/Anwitch/Phosor/issues)
- 💬 Start a [Discussion](https://github.com/Anwitch/Phosor/discussions)

---

## 📜 License

This project is licensed under the MIT License – see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using Python, FastAPI, UniFace, and Alpine.js**

[⭐ Star this repo](https://github.com/Anwitch/Phosor) if you find it useful!

</div>
