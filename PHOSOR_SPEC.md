# Phosor – Project Specification

**Photo Sorting Orchestrator for Faces**

Version: 1.0.0  
Last Updated: December 1, 2025

---

## Overview

Phosor is a Python-based photo clustering tool that automatically organizes photos by detecting and grouping faces using facial recognition. It combines a CLI pipeline with a web dashboard for managing clusters.

---

## Features

### Core Features (CLI)

1. **Image Scanning**
   - Recursive directory scanning
   - Support for JPG, JPEG, PNG, WebP
   - Configurable file size filtering

2. **Face Detection & Embedding**
   - UniFace integration for face detection
   - 512-dimensional face embeddings
   - Batch processing with progress tracking

3. **Clustering**
   - DBSCAN algorithm with cosine distance
   - Configurable clustering parameters (eps, min_samples)
   - Automatic cluster labeling (Person_01, Person_02, etc.)
   - Minimum faces per cluster filtering

4. **Output Management**
   - Copy or move files to cluster folders
   - Representative face image generation (crop/bbox/annotated modes)
   - JSON metadata export (embeddings.json, clusters_summary.json)
   - Unclustered images handling

### Web Dashboard Features

1. **Cluster Management**
   - View all clusters with statistics
   - Alphabetically sorted cluster grid
   - Create new clusters
   - Rename clusters (inline edit + modal)
   - Delete clusters (with double confirmation)
   - Merge multiple clusters

2. **Image Management**
   - View cluster images in responsive gallery
   - Lightbox for full-size viewing
   - Delete individual images
   - Copy unclustered images to clusters (single or multiple)
   - Representative thumbnail display

3. **User Interface**
   - Responsive design (mobile to desktop)
   - Real-time statistics (clusters, faces, images)
   - Search functionality in modals
   - Loading and error states
   - Keyboard navigation in lightbox

4. **Performance**
   - 24-hour browser caching for images
   - Immutable cache headers
   - Efficient file serving

---

## Architecture

### Technology Stack

**Backend:**
- Python 3.10+
- FastAPI 0.123.0
- Uvicorn (ASGI server)
- Jinja2 3.1.6 (templating)
- UniFace (face detection/recognition)
- scikit-learn (DBSCAN clustering)

**Frontend:**
- Alpine.js 3.x (reactivity)
- Tailwind CSS 3.4.1 (styling)
- Server-side rendering

**Storage:**
- JSON files for metadata
- Filesystem for images

### Project Structure

```
phosor/
├── src/
│   ├── core/                    # CLI pipeline
│   │   ├── cli.py              # Typer commands
│   │   ├── config.py           # Configuration handling
│   │   ├── models.py           # Data models
│   │   ├── file_scanner.py     # Image discovery
│   │   ├── face_engine.py      # UniFace wrapper
│   │   ├── clustering.py       # DBSCAN clustering
│   │   ├── folder_manager.py   # Output operations
│   │   └── utils.py            # Utilities
│   │
│   └── frontend/               # Web dashboard
│       ├── app.py              # FastAPI application
│       ├── api/
│       │   ├── clusters.py     # Cluster endpoints
│       │   └── images.py       # Image serving
│       └── templates/
│           ├── base.html       # Layout
│           ├── index.html      # Dashboard
│           └── cluster_detail.html  # Cluster view
│
├── configs/
│   └── config.toml             # Configuration file
├── tests/                       # Unit tests
└── pyproject.toml              # Dependencies
```

---

## API Endpoints

### Cluster Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clusters` | List all clusters with statistics |
| GET | `/api/clusters/{cluster_id}` | Get cluster details |
| GET | `/api/clusters/{cluster_id}/images` | List images in cluster |
| POST | `/api/clusters` | Create new cluster |
| PATCH | `/api/clusters/{cluster_id}` | Update cluster label |
| POST | `/api/clusters/merge` | Merge multiple clusters |
| DELETE | `/api/clusters/{cluster_id}` | Delete cluster |

### Image Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/images/representative/{cluster}` | Serve representative image |
| GET | `/api/images/{cluster}/{filename}` | Serve cluster image |
| GET | `/api/images/unclustered/{filename}` | Serve unclustered image |
| POST | `/api/images/move-multiple` | Copy image to clusters |
| DELETE | `/api/images/{cluster_id}/{filename}` | Delete image |

### Unclustered Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/unclustered` | List unclustered images |

**Total Endpoints:** 13

---

## Configuration

Configuration via `config.toml`:

```toml
[input]
dir = "path/to/input"
recursive = true
min_file_size_kb = 50

[output]
dir = "path/to/output"
mode = "copy"  # or "move"

[clustering]
method = "dbscan"
eps = 0.5
min_samples = 3
min_faces_per_cluster = 3

[representative]
mode = "crop"  # crop, bbox, annotated
thumbnail_size = 200

[handling]
include_no_face = false
save_embeddings = true

[logging]
level = "INFO"
file = "logs/phosor.log"
```

---

## CLI Commands

```bash
# Scan and cluster images
phosor scan --input-dir /path/to/photos --output-dir /path/to/output

# View clustering summary
phosor summary /path/to/output/clusters_summary.json

# Start web dashboard
phosor serve --host 127.0.0.1 --port 8000 --reload
```

---

## Data Models

### FaceRecord
```python
{
    "id": int,
    "image_path": str,
    "face_index": int,
    "bbox": [x, y, w, h],
    "embedding": [512-dim array],
    "cluster_id": int | -1
}
```

### ClusterSummary
```python
{
    "cluster_id": int,
    "label": str,
    "num_faces": int,
    "num_images": int,
    "sample_images": [str, str, str]
}
```

---

## Dependencies

```toml
[project.dependencies]
uniface = "^0.1.0"
opencv-python = "^4.8.0"
numpy = "^1.24.0"
scikit-learn = "^1.3.0"
tqdm = "^4.66.0"
typer = "^0.9.0"
pydantic = "^2.0.0"
fastapi = "^0.123.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
jinja2 = "^3.1.6"
python-multipart = "^0.0.6"
aiofiles = "^23.0.0"

[project.optional-dependencies]
dev = ["pytest", "black", "ruff"]
```

---

## Testing

- **19/19 tests passing**
- Test coverage: file_scanner, clustering, folder_manager
- Real-world test: 78 images, 400 faces, 20 clusters

---

## Deployment

### Development
```bash
# Activate environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run server with auto-reload
phosor serve --reload
```

### Production
```bash
# Run on all interfaces
phosor serve --host 0.0.0.0 --port 8000

# Or with uvicorn directly
uvicorn frontend.app:app --host 0.0.0.0 --port 8000
```

### Recommended Production Setup
- Reverse proxy: nginx
- Process manager: systemd or supervisor
- Authentication: Add if exposing to internet
- HTTPS: Use Let's Encrypt certificates

---

## License & Credits

- Built with Python, FastAPI, Alpine.js, Tailwind CSS
- Face detection: UniFace
- Clustering: scikit-learn DBSCAN
