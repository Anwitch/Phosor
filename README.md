# Phosor 🧠📸

**Photo Sorting Orchestrator for Faces**

Automated face-based photo clustering and organization system.

## Overview

Phosor automatically groups photos by detected faces using state-of-the-art face recognition. It scans a folder of photos, detects faces, generates embeddings, performs clustering, and organizes photos into per-person folders.

**Target Users:**
- Event photographers (weddings, graduations, conferences)
- Documentation teams
- Anyone managing large photo collections

## Features

- 🔍 **Automatic Face Detection** - Powered by UniFace
- 🎯 **Smart Clustering** - Groups similar faces using DBSCAN/KMeans
- 📁 **Organized Output** - Creates folders per person/cluster
- 🚀 **Local Processing** - All data stays on your device
- ⚙️ **Configurable** - Customizable clustering parameters
- 🧪 **Dry Run Mode** - Preview results before moving files

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Phosor
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

## Quick Start

1. **Place photos** in `data/input/` folder

2. **Run Phosor:**
   ```bash
   phosor scan --input data/input --output data/output
   ```

3. **Check results** in `data/output/`:
   - `Person_01/`, `Person_02/`, etc. - Clustered photos
   - `unclustered/` - Faces that couldn't be grouped
   - `clusters_summary.json` - Statistics

## Usage

### Basic Scan
```bash
phosor scan --input /path/to/photos --output /path/to/results
```

### With Config File
```bash
phosor scan --config configs/config.toml
```

### Dry Run (Preview Only)
```bash
phosor scan --input data/input --output data/output --dry-run
```

### View Summary
```bash
phosor summary data/output/clusters_summary.json
```

## Configuration

Create a `config.toml` file (see `configs/config.example.toml`):

```toml
[input]
dir = "data/input"
recursive = true
min_file_size_kb = 50

[output]
dir = "data/output"
mode = "copy"  # or "move"

[clustering]
method = "dbscan"
eps = 0.5
min_samples = 3
min_faces_per_cluster = 5

[logging]
level = "INFO"
file = "logs/phosor.log"
```

## Project Structure

```
Phosor/
├── src/core/           # Core application code
│   ├── cli.py          # Command-line interface
│   ├── face_engine.py  # Face detection/embedding
│   ├── clustering.py   # Clustering logic
│   ├── file_scanner.py # Image file discovery
│   ├── folder_manager.py # Output organization
│   ├── config.py       # Configuration handling
│   ├── models.py       # Data models
│   └── utils.py        # Utilities
├── configs/            # Configuration files
├── data/
│   ├── input/         # Input photos
│   └── output/        # Results
├── logs/              # Application logs
├── tests/             # Unit tests
└── pyproject.toml     # Project metadata
```

## Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black src/ tests/
```

### Lint Code
```bash
ruff check src/ tests/
```

## Roadmap

- [x] Phase 1: Core MVP (CLI + Pipeline)
- [ ] Phase 2: Incremental updates with hash tracking
- [ ] Phase 3: SQLite metadata storage
- [ ] Phase 4: Web dashboard (FastAPI)
- [ ] Phase 5: Manual cluster merge/split UI

## Technical Details

- **Python:** 3.10+
- **Face Detection:** UniFace (RetinaFace + ArcFace)
- **Clustering:** scikit-learn (DBSCAN/KMeans)
- **CLI:** Typer + Rich

## License

[Your License Here]

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## Support

For issues and questions, please open a GitHub issue.
