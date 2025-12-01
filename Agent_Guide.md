# Phosor – AI Agent Vibe Coding Steps

This document describes **clear, small, sequential steps** for an AI coding agent to implement *Phosor* (Photo Sorting Orchestrator for Faces) based on the project concept. The agent must follow these steps gradually, keep code clean, and avoid skipping milestones.

---

## 0. Global Rules for the AI Agent

1. **Language & Stack**

   * Use **Python 3.10+**.
   * Use **uv / pip + venv** or **poetry** for dependency management.
2. **Code Quality**

   * Write code with type hints.
   * Keep functions small and single‑responsibility.
   * Add minimal but clear docstrings.
3. **Commit Style (if under Git)**

   * After each major step, prepare a logical commit (message like `feat: add file scanner`, `feat: basic face engine wrapper`, etc.).
4. **Do Not Over‑Engineer**

   * Focus on making **MVP CLI + core pipeline** work first.
   * Advanced features (incremental update, DB, dashboard) are *later phases*.
5. **Always Update ur Progress**

   * After each step, **update this document** with ✅ or ❌ to mark completion.
---

## 1. Project Bootstrap

**Goal:** Create a clean Python project structure with tooling, no real logic yet.

### 1.1 Initialize Repo & Environment ✅

Steps for the agent:

1. Create a new project folder named `phosor`.
2. Initialize a Python project:

   * Add `pyproject.toml` (or `requirements.txt` if simpler) including at least:

     * `uniface`
     * `opencv-python`
     * `numpy`
     * `scikit-learn`
     * `tqdm`
     * `typer`
     * `pydantic`
     * `pytest`
     * `black`
     * `ruff`
3. Add basic Git ignore file for Python (`.venv`, `__pycache__`, etc.).

### 1.2 Create Base Package Structure ✅

Steps for the agent:

1. Inside project, create package tree:

   * `src/core/__init__.py`
   * `src/core/cli.py`
   * `src/core/face_engine.py`
   * `src/core/clustering.py`
   * `src/core/file_scanner.py`
   * `src/core/folder_manager.py`
   * `src/core/config.py`
   * `src/core/models.py`
   * `src/core/utils.py`
2. Create extra folders:

   * `configs/` with `config.example.toml`.
   * `data/input/` and `data/output/` (empty example folders, maybe with README stub).
   * `logs/` (empty, with README stub).
   * `tests/` with empty test files matching modules.
3. Add placeholder content for each module (minimal classes/functions + `pass`) just to make imports valid.

### 1.3 Setup CLI Entry Point ✅

Steps for the agent:

1. Use `typer` to create a `Typer` app in `src/core/cli.py` with at least commands:

   * `scan`
   * `summary`
2. Wire `scan` command signature like:

   ```python
   def scan(
       input_dir: str = typer.Option(..., help="Input folder with images"),
       output_dir: str = typer.Option(..., help="Output folder for clusters"),
       config: Optional[str] = typer.Option(None, help="Path to config file"),
       dry_run: bool = typer.Option(False, help="Run without copying/moving files"),
   ):
       """Run full Phosor pipeline: scan → embed → cluster → write output."""
   ```
3. Configure `pyproject.toml` (or `setup.cfg`) to expose console script:

   * `phosor = core.cli:app` (Typer app).
4. Add a minimal `main()` or `if __name__ == "__main__":` section if needed for direct execution.

---

## 2. Config & Models Layer ✅

**Goal:** Define data models & configuration handling before touching real logic.

### 2.1 Define Core Data Models ✅

Steps for the agent (in `src/core/models.py`):

1. Create `ImageRecord` model:

   * Fields:

     * `id: int`
     * `image_path: str`
     * `hash: Optional[str]`
2. Create `FaceRecord` model:

   * Fields:

     * `id: int`
     * `image_path: str`
     * `face_index: int`
     * `bbox: tuple[int, int, int, int]`
     * `embedding: list[float]` or `np.ndarray`
     * `cluster_id: Optional[int]`
3. Create `ClusterSummary` model:

   * Fields:

     * `cluster_id: int`
     * `label: str`
     * `num_faces: int`
     * `sample_images: list[str]`
4. Implement these models as `pydantic.BaseModel` or dataclasses, depending on what is simpler for the agent.

### 2.2 Implement Configuration Handling ✅

Steps for the agent (in `src/core/config.py`):

1. Create `PhosorConfig` settings model (using Pydantic or similar) with sections:

   * `input.dir: str`
   * `input.recursive: bool`
   * `output.dir: str`
   * `output.mode: Literal["copy", "move"]`
   * `clustering.method: Literal["dbscan", "kmeans"]`
   * `clustering.eps: float`
   * `clustering.min_samples: int`
   * `clustering.min_faces_per_cluster: int`
   * `handling.include_no_face: bool`
   * `handling.save_embeddings: bool`
   * `logging.level: str`
   * `logging.file: str`
2. Implement function `load_config(path: Optional[str]) -> PhosorConfig` that:

   * Reads TOML if path provided.
   * If not provided, loads default values.
   * Allows environment overrides if needed.
3. Fill `configs/config.example.toml` following the config structure from the concept doc.

### 2.3 Wire Config into CLI ✅

Steps for the agent (in `src/core/cli.py`):

1. In `scan()`:

   * If `config` path is given → load config using `load_config`.
   * Override `input_dir` / `output_dir` if CLI args are provided.
2. Ensure `scan()` logs final resolved settings (input, output, clustering mode, etc.).

---

## 3. File Scanner Implementation ✅

**Goal:** Turn a directory into a clean list of valid image paths.

### 3.1 Implement File Scanner ✅

Steps for the agent (in `src/core/file_scanner.py`):

1. Implement function:

   ```python
   def scan_images(input_dir: str, recursive: bool = True, min_file_size_kb: int = 50) -> list[str]:
       """Return list of image file paths under input_dir matching allowed extensions and size."""
   ```
2. Behavior:

   * Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.webp` (lower/upper case).
   * Skip files smaller than `min_file_size_kb`.
   * If `recursive` is true, walk subdirectories.
3. Add minimal logging using `logging` module.
4. Add unit test in `tests/test_file_scanner.py` with few fake files.

### 3.2 Integrate Scanner into CLI ✅

Steps for the agent (in `src/core/cli.py`):

1. In `scan()`:

   * Call `scan_images(config.input.dir, config.input.recursive, config.input.min_file_size_kb)`.
   * Log number of discovered images.

---

## 4. Face Engine Wrapper (UniFace) ✅

**Goal:** Wrap UniFace to provide a simple API: detect faces and get embeddings.

### 4.1 Implement FaceEngine Class ✅

Steps for the agent (in `src/core/face_engine.py`):

1. Create class `FaceEngine` with:

   * `__init__` to initialize required UniFace models only once.
   * Method `detect_faces(image: np.ndarray) -> list[dict]`:

     * Returns list with at least `bbox` and `landmarks`.
   * Method `embed_face(image: np.ndarray, face: dict) -> np.ndarray`:

     * Uses UniFace to compute embedding.
2. Add small abstraction so underlying UniFace implementation can be swapped in future.
3. Handle errors gracefully:

   * If detection fails → return empty list.
   * If embedding fails for a face → skip that face, log warning.

### 4.2 Implement Single‑Image Processing Helper ✅

Steps for the agent (in `src/core/face_engine.py` or `src/core/utils.py`):

1. Implement function `process_image(image_path: str, engine: FaceEngine) -> list[FaceRecord]`:

   * Load image using `cv2.imread`.
   * Run `engine.detect_faces`.
   * For each detected face, compute embedding.
   * Return list of `FaceRecord` instances.
2. If `cv2.imread` returns `None`, log error and return empty list.

---

## 5. Embedding Collection Pipeline ✅

**Goal:** For a batch of image paths, produce a list of FaceRecord objects.

### 5.1 Implement Batch Processing ✅

Steps for the agent (new module or `utils.py`):

1. Implement function:

   ```python
   def build_face_dataset(image_paths: list[str], engine: FaceEngine) -> list[FaceRecord]:
       """Process all images and return list of FaceRecord with embeddings."""
   ```
2. Use `tqdm` progress bar around loop over images.
3. Aggregate all `FaceRecord` from all images into one list.
4. Assign incremental IDs to faces.

### 5.2 Add Minimal Tests ✅

Steps for the agent:

1. Write a small unit/integration test that mocks `FaceEngine` methods to avoid real heavy model loading.
2. Ensure the function correctly flattens multiple images & faces into a single list of `FaceRecord`.

---

## 6. Clustering Logic ✅

**Goal:** Cluster embeddings into groups using DBSCAN by default.

### 6.1 Implement Clustering Engine ✅

Steps for the agent (in `src/core/clustering.py`):

1. Implement function:

   ```python
   def cluster_faces(
       faces: list[FaceRecord],
       method: str = "dbscan",
       eps: float = 0.5,
       min_samples: int = 3,
   ) -> list[FaceRecord]:
       """Assign cluster_id to face records and return updated list."""
   ```
2. Details:

   * Build 2D array of embeddings from `faces`.
   * For DBSCAN:

     * Use cosine distance (`metric="cosine"`).
   * After clustering, set `face.cluster_id` to label returned by algorithm.
3. Treat cluster label `-1` as noise (unclustered faces).

### 6.2 Cluster Summary Builder ✅

Steps for the agent (in `src/core/clustering.py` or `utils.py`):

1. Implement function:

   ```python
   def build_cluster_summary(faces: list[FaceRecord]) -> list[ClusterSummary]:
       """Aggregate faces per cluster into summary models."""
   ```
2. For each non‑noise cluster:

   * Count number of faces.
   * Collect sample image paths (e.g. first 3 unique images).
   * Generate label like `Person_01`, `Person_02`, etc.

---

## 7. Output Writer (Folders + Metadata) ✅

**Goal:** Take clustered data and materialize it into folder structure and JSON files.

### 7.1 Folder Manager ✅

Steps for the agent (in `src/core/folder_manager.py`):

1. Implement function:

   ```python
   def prepare_output_dirs(base_output_dir: str, clusters: list[ClusterSummary], include_unclustered: bool = True) -> dict[int, str]:
       """Create cluster folders and return mapping cluster_id -> folder path."""
   ```
2. For each `ClusterSummary`, create a folder:

   * e.g. `<output_dir>/Person_01`, `<output_dir>/Person_02`, etc.
3. Create special folders:

   * `unclustered/` for faces with cluster `-1`.
   * Optionally `no_face/` if configured.

### 7.2 Copy / Move Files According to Cluster ✅

Steps for the agent (in `src/core/folder_manager.py`):

1. Implement function:

   ```python
   def materialize_clusters(
       faces: list[FaceRecord],
       cluster_summaries: list[ClusterSummary],
       output_dir: str,
       mode: str = "copy",
       dry_run: bool = False,
   ) -> None:
       """Copy or move image files into cluster folders according to assigned cluster_id."""
   ```
2. Behavior:

   * Use mapping `cluster_id -> folder path`.
   * For each face, ensure its source image is copied/moved once per cluster (per unique image path).
   * Avoid duplicating the same image multiple times in same folder.
   * If `dry_run` is true, **do not** touch filesystem, only log planned actions.

### 7.3 Save Metadata JSON ✅

Steps for the agent (in `src/core/utils.py` or dedicated module):

1. Implement function to save:

   * Full list of faces with embeddings & cluster ids → `embeddings.json`.
   * Cluster summaries → `clusters_summary.json`.
2. Use standard `json` module.
3. Make sure data is serializable (convert numpy arrays to lists).

---

## 8. Wiring Full Pipeline in CLI `scan` ✅

**Goal:** Connect all core components into a working `phosor scan` command.

### 8.1 Implement Full Flow ✅

Steps for the agent (in `src/core/cli.py`):

1. In `scan()` perform steps in order:

   1. Load config.
   2. Resolve `input_dir` & `output_dir`.
   3. Scan image files.
   4. Initialize `FaceEngine`.
   5. Build face dataset from image list.
   6. Run clustering.
   7. Build cluster summary.
   8. Prepare output directories.
   9. Materialize folders (copy/move) unless `dry_run`.
   10. Save metadata JSON.
2. Add clear log messages at each phase so user knows progress.
3. Exit with non‑zero code if fatal errors (e.g. no images found, or no faces at all).

---

## 9. `summary` Command Implementation ✅

**Goal:** Provide a simple way to inspect cluster results from JSON after a run.

Steps for the agent (in `src/core/cli.py`):

1. Implement `summary` command with argument:

   ```python
   def summary(metadata: str = typer.Argument(..., help="Path to clusters_summary.json")):
   ```
2. Steps:

   * Load `clusters_summary.json`.
   * Print table/report:

     * Cluster ID, label, number of faces, number of unique images.
     * Count of unclustered faces (if included in file).
3. Optionally use `rich` to pretty‑print table if already in dependencies.

---

## 10. Basic Tests & Tooling ✅

**Goal:** Ensure project doesn't rot immediately.

### 10.1 Minimal Test Suite ✅

Steps for the agent:

1. Add tests for:

   * `scan_images` behavior.
   * Clustering function with synthetic embeddings.
   * Folder manager (use temporary directories).
2. Configure `pytest` in `pyproject.toml` or `pytest.ini`.

### 10.2 Formatting & Linting ✅

Steps for the agent:

1. Configure `black` & `ruff` in `pyproject.toml`.
2. Ensure code passes format + lint.

---

## ✅ PHASES 1-10 COMPLETE!

**All core features implemented and tested!**

### Additional Features Implemented:

1. **Representative Face Images** ✅
   - Added `create_cluster_representatives()` function in `folder_manager.py`
   - Three visualization modes: crop, bbox, annotated
   - Each cluster folder gets `_representative.jpg` file
   - Configurable via `config.toml`
   - Integrated into Step 6/7 of scan pipeline

2. **Windows Path Normalization** ✅
   - Enhanced `load_config()` with path preprocessing
   - Added Pydantic validators for path normalization
   - Supports all Windows path formats (backslash, forward slash, escaped)
   - Users can copy-paste paths directly from File Explorer

### Test Results:
- **19/19 tests passing** ✅
- Successfully processed real dataset: 78 images, 400 faces, 20 clusters
- All features working in production

---

## 11. Web Dashboard (MVP) 🚧

**Goal:** Create a simple web interface to review clustering results and manage clusters.

**Status:** PLANNED - Ready to implement

---

### ⚙️ Prerequisites - HUMAN MUST DO FIRST!

**Before the AI agent starts implementing Section 11, the human developer must:**

#### 1. Install Web Dependencies
```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/Mac

# Install FastAPI and related packages
pip install fastapi uvicorn[standard] jinja2 python-multipart aiofiles

# Update requirements or pyproject.toml
pip freeze > requirements.txt
# OR if using pyproject.toml, add to [project.dependencies]:
# fastapi = "^0.104.0"
# uvicorn = {extras = ["standard"], version = "^0.24.0"}
# jinja2 = "^3.1.0"
# python-multipart = "^0.0.6"
# aiofiles = "^23.0.0"
```

#### 2. Verify Installation
```bash
# Test if FastAPI is installed correctly
python -c "from fastapi import FastAPI; print('FastAPI OK')"
python -c "import uvicorn; print('Uvicorn OK')"
python -c "import jinja2; print('Jinja2 OK')"
```

#### 3. Create Directory Structure
```bash
# Create frontend directories (AI will populate these)
mkdir src\frontend
mkdir src\frontend\api
mkdir src\frontend\templates
mkdir src\frontend\templates\components
mkdir src\frontend\static
mkdir src\frontend\static\css
mkdir src\frontend\static\js

# Create __init__.py files
type nul > src\frontend\__init__.py
type nul > src\frontend\api\__init__.py

# Linux/Mac equivalent:
# mkdir -p src/frontend/{api,templates/components,static/{css,js}}
# touch src/frontend/__init__.py src/frontend/api/__init__.py
```

#### 4. Verify Current Setup
```bash
# Make sure CLI is still working
phosor --help

# Check if you have existing output to test with
dir C:\Users\Andri\Downloads\TestingPhosor\output
# Should see: clusters_summary.json, embeddings.json, Person_* folders
```

#### 5. Optional: Test Data Validation
```bash
# Ensure you have valid clustering results to display in web UI
phosor summary C:\Users\Andri\Downloads\TestingPhosor\output\clusters_summary.json

# This should show your 20 clusters - web UI will display these
```

#### 6. Checklist Before Starting ✅
- [ ] FastAPI, uvicorn, jinja2 installed
- [ ] `src/frontend/` directory structure created
- [ ] Existing Phosor CLI still working (`phosor --help`)
- [ ] Have valid output data (clusters_summary.json exists)
- [ ] Virtual environment activated
- [ ] Git status clean (optional but recommended)

**Once all above steps are done, tell the AI agent: "Prerequisites done, start implementing Section 11.1"**

---

### Architecture Decision

**Backend:** FastAPI
- Modern Python async framework
- Auto-generated OpenAPI docs
- Easy to integrate with existing Python codebase
- Built-in validation with Pydantic (already used in project)
- Fast development cycle

**Frontend:** HTML + Tailwind CSS + Alpine.js (Hyperscript approach)
- No complex build tools needed (MVP approach)
- Tailwind via CDN for rapid styling
- Alpine.js for interactivity (lightweight, Vue-like syntax)
- Server-side rendering with Jinja2 templates
- Progressive enhancement: works without JS, better with JS

**File Structure:**
```
src/
├── core/              # Existing CLI modules
└── frontend/          # NEW: Web application
    ├── __init__.py
    ├── app.py         # FastAPI application
    ├── api/           # API endpoints
    │   ├── __init__.py
    │   ├── clusters.py    # Cluster management
    │   └── images.py      # Image serving
    ├── templates/     # Jinja2 HTML templates
    │   ├── base.html
    │   ├── index.html
    │   ├── cluster_detail.html
    │   └── components/
    └── static/        # CSS, JS, icons
        ├── css/
        └── js/
```

### 11.1 Setup FastAPI Backend ✅

**Dependencies to add in `pyproject.toml`:**
```toml
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
jinja2 = "^3.1.0"
python-multipart = "^0.0.6"  # For file uploads
aiofiles = "^23.0.0"  # For async file operations
```

**Steps for the agent (in `src/frontend/app.py`):**

1. Create FastAPI app instance:
   ```python
   from fastapi import FastAPI
   from fastapi.staticfiles import StaticFiles
   from fastapi.templating import Jinja2Templates
   
   app = FastAPI(title="Phosor Dashboard", version="1.0.0")
   app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")
   templates = Jinja2Templates(directory="src/frontend/templates")
   ```

2. Add CORS middleware for development:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(CORSMiddleware, allow_origins=["*"])
   ```

3. Create startup configuration:
   - Load Phosor config on startup
   - Store output directory path in app state
   - Initialize logging

4. Add CLI command in `src/core/cli.py`:
   ```python
   @app.command()
   def serve(
       host: str = "127.0.0.1",
       port: int = 8000,
       reload: bool = False,
   ):
       """Start web dashboard server."""
       import uvicorn
       uvicorn.run("frontend.app:app", host=host, port=port, reload=reload)
   ```

### 11.2 Implement Core API Endpoints ✅

**COMPLETED:** All API endpoints implemented and tested successfully.

**Implemented in `src/frontend/api/clusters.py`:**

1. ✅ **GET /api/clusters** - List all clusters
   - Reads `clusters_summary.json` from configured output directory
   - Returns list of `ClusterInfo` models with actual image counts from filesystem
   - Handles both `{"clusters": [...]}` and `[...]` JSON formats

2. ✅ **GET /api/clusters/{cluster_id}** - Get cluster details
   - Returns detailed info: label, face count, actual image count, sample images
   - Counts real files in folder (excluding `_representative.jpg`)

3. ✅ **GET /api/clusters/{cluster_id}/images** - List images in cluster
   - Returns list of all image files with filename, path, and size
   - Excludes representative image from listing

4. ✅ **PATCH /api/clusters/{cluster_id}** - Update cluster label
   - Renames cluster (e.g., Person_01 → John Doe)
   - Updates `clusters_summary.json`
   - Renames folder on filesystem atomically
   - Validates new label doesn't exist

5. ✅ **POST /api/clusters/merge** - Merge clusters
   - Merges multiple clusters into target cluster
   - Moves all images to target folder
   - Handles filename conflicts with counter suffix
   - Updates metadata and removes source cluster folders

**Implemented in `src/frontend/api/images.py`:**

1. ✅ **GET /api/images/{cluster_label}/{filename}** - Serve images
   - Serves image files from cluster folders using `FileResponse`
   - **Critical:** Generic route placed AFTER specific routes to avoid route collision

2. ✅ **GET /api/images/representative/{cluster_label}** - Get representative image
   - Serves `_representative.jpg` for cluster
   - **Critical:** Must be defined BEFORE generic route due to FastAPI route matching order
   - Fallback to first image if representative missing
   - Includes debug logging for troubleshooting

### 11.3 Build Web UI Templates ✅

**COMPLETED:** All core templates implemented with Alpine.js interactivity.

**Base Layout (`templates/base.html`):** ✅
- HTML5 boilerplate with responsive viewport
- Tailwind CSS 3.4.1 via CDN
- Alpine.js 3.x via CDN
- Common navigation header with project branding
- Footer with version info and technology credits
- Template blocks for title, content, and scripts

**Dashboard Home (`templates/index.html`):** ✅

**Implemented Features:**
1. ✅ **Overview Statistics Card**
   - Total Clusters count
   - Total Detections (face count across all clusters)
   - Total Images (actual file count from folders)
   - Responsive grid layout (1-3 columns)

2. ✅ **Cluster Grid View**
   - Responsive grid: 1 column (mobile) → 4 columns (desktop)
   - Each card displays:
     - Representative image with error fallback (SVG placeholder)
     - Cluster label (editable via rename modal)
     - Image count (actual files from folder)
     - View and Rename action buttons
   - Hover effects and smooth transitions
   - Empty state when no clusters found

3. ✅ **Quick Actions**
   - Refresh button to reload cluster data
   - Real-time statistics calculation from API data

4. ✅ **Rename Modal**
   - Click "Rename" button to open modal
   - Shows current label
   - Input for new label with validation
   - Updates both JSON metadata and filesystem folder
   - Auto-refreshes grid after successful rename
   - Loading state during operation

5. ✅ **Alpine.js State Management**
   ```javascript
   - loading: boolean (shows spinner during API calls)
   - error: string | null (displays error messages)
   - clusters: array (cluster data from API)
   - stats: { totalClusters, totalFaces, totalImages }
   - renameModal: { show, cluster, newLabel, loading }
   ```

**Cluster Detail Page (`templates/cluster_detail.html`):** ✅

**Implemented Features:**
1. ✅ **Cluster Header**
   - Back to dashboard link with navigation
   - Editable cluster name (inline edit with pencil icon)
   - Metadata display (image count)
   - Clean, minimal design

2. ✅ **Image Gallery**
   - Responsive grid (2-6 columns based on screen size)
   - Thumbnail images with aspect-ratio containers
   - Error fallback for broken images
   - Click to open lightbox (full-size view)
   - Loading state during API fetch
   - Error state with retry option

3. ✅ **Lightbox Feature**
   - Full-screen modal for viewing images
   - Dark backdrop (black/75% opacity)
   - Keyboard navigation:
     - Arrow Left/Right: Previous/Next image
     - Escape: Close lightbox
   - Click outside to close
   - Large image display with max-height constraint
   - Navigation arrows (Previous/Next buttons)
   - Close button (X icon)

4. ✅ **JavaScript Syntax Fixes**
   - Fixed indentation issues in Alpine.js object
   - Corrected property alignment in `x-data` declaration
   - All functions properly formatted and working

5. ✅ **Alpine.js Component**
   ```javascript
   - images: array (loaded from API)
   - loading: boolean
   - error: string | null
   - editing: boolean (for label edit mode)
   - editedLabel: string (new label value)
   - lightbox: { show, currentIndex, image }
   - Functions:
     - loadImages(): Fetch images from API
     - startEdit(): Enter edit mode
     - saveLabel(): PATCH request to update label
     - openLightbox(index): Open image viewer
     - closeLightbox(): Close viewer
     - nextImage(): Navigate to next
     - prevImage(): Navigate to previous
   ```

**Key Implementation Details:**
- ✅ Route ordering fix: `/images/representative/{cluster}` defined BEFORE `/images/{cluster}/{filename}` in `images.py`
- ✅ Fallback logic: Uses first image if `_representative.jpg` missing
- ✅ Error handling: SVG placeholders for missing images
- ✅ Path resolution: Proper Windows path handling with forward slashes
- ✅ Responsive design: Mobile-first with progressive enhancement

### 11.4 Add Interactivity with Alpine.js ✅

**COMPLETED:** Core interactivity features implemented and working.

**Implemented Features:**

1. ✅ **Inline Label Editing (Cluster Detail Page)**
   ```html
   <div x-data="{ editing: false, editedLabel: cluster.label }">
     <!-- Display mode: click pencil to edit -->
     <h1 x-show="!editing" class="text-3xl font-bold">
       <span x-text="cluster.label"></span>
       <button @click="startEdit()">✏️</button>
     </h1>
     
     <!-- Edit mode: input with save/cancel -->
     <div x-show="editing">
       <input x-model="editedLabel" @keyup.enter="saveLabel()" />
       <button @click="saveLabel()">Save</button>
       <button @click="editing = false">Cancel</button>
     </div>
   </div>
   ```
   - **Implementation:** Click pencil icon → input appears → Enter or Save → PATCH request → updates both JSON and folder name

2. ✅ **Image Gallery with Lightbox**
   ```html
   <div x-data="{ lightbox: { show: false, currentIndex: 0, image: null } }">
     <!-- Gallery grid -->
     <img @click="openLightbox(index)" />
     
     <!-- Lightbox modal with keyboard navigation -->
     <div x-show="lightbox.show" @keydown.escape.window="closeLightbox()"
          @keydown.arrow-left.window="prevImage()"
          @keydown.arrow-right.window="nextImage()">
       <img :src="lightbox.image" />
       <button @click="prevImage()">←</button>
       <button @click="nextImage()">→</button>
     </div>
   </div>
   ```
   - **Implementation:** Full-screen modal, keyboard navigation (Esc/Arrows), click outside to close

3. ✅ **Cluster Rename Modal (Dashboard)**
   ```html
   <div x-data="{ renameModal: { show: false, cluster: null, newLabel: '' } }">
     <button @click="startRename(cluster)">Rename</button>
     
     <!-- Modal with form -->
     <div x-show="renameModal.show" @click.self="closeRenameModal()">
       <input x-model="renameModal.newLabel" @keyup.enter="submitRename()" />
       <button @click="submitRename()">Rename</button>
     </div>
   </div>
   ```
   - **Implementation:** Modal overlay, PATCH to `/api/clusters/{id}`, updates filesystem and JSON, refreshes cluster list

4. ✅ **Real-time Statistics**
   ```javascript
   calculateStats() {
     this.stats.totalClusters = this.clusters.length;
     this.stats.totalFaces = this.clusters.reduce((sum, c) => sum + c.num_faces, 0);
     this.stats.totalImages = this.clusters.reduce((sum, c) => sum + c.num_images, 0);
   }
   ```
   - **Implementation:** Calculates from API response, updates dashboard cards

5. ✅ **Loading & Error States**
   - Loading spinner during API calls
   - Error messages with red background
   - Empty state when no clusters found
   - Disabled buttons during async operations

**Key Fixes Applied:**
- ✅ Fixed JavaScript syntax errors (indentation in Alpine.js objects)
- ✅ Proper event handling with `@click`, `@keyup`, `@keydown`
- ✅ Reactive state management with `x-show`, `x-model`, `x-text`
- ✅ Async/await patterns for API calls
- ✅ Error handling with try-catch blocks

### 11.5 Advanced Features (Optional) 📋

**Current Status:** Basic features complete, advanced features pending.

**Implemented:**
- ✅ Cluster renaming (inline edit + modal)
- ✅ Image gallery with lightbox
- ✅ Statistics dashboard
- ✅ Representative image display

**Pending (Future Enhancements):**

1. **Cluster Merging UI** 🔨
   - Currently: API endpoint exists (`POST /api/clusters/merge`)
   - TODO: Build modal UI for selecting source and target clusters
   - TODO: Add confirmation dialog
   - TODO: Show merge preview (combined image count)

2. **Filtering and Sorting**
   - TODO: Search box to filter clusters by name
   - TODO: Sort dropdown (by size, label, date)
   - TODO: Alpine.js computed properties for filtered list

3. **WebSocket for Real-time Updates** 💡
   - Show scan progress live
   - Update UI when new clusters created
   - Requires: `websockets` library

4. **Face Recognition Search** 💡
   - Upload a face photo
   - Find all images containing that person
   - Use existing embeddings for comparison

5. **Cluster Quality Score** 💡
   - Show confidence/cohesion metric
   - Highlight clusters needing review
   - Based on embedding distances

6. **Batch Operations** 💡
   - Select multiple clusters
   - Bulk rename (e.g., "Person_01..05" → "John's Photos")
   - Bulk merge/delete

7. **Export Functions** 💡
   - Download cluster as ZIP
   - Export metadata to CSV
   - Share cluster (generate public link)

**Known Issues Fixed:**
- ✅ Route ordering bug (representative images 404) - RESOLVED
- ✅ JavaScript syntax errors in cluster_detail.html - RESOLVED
- ✅ Non-sequential cluster numbering - RESOLVED
- ✅ Incorrect image count display - RESOLVED
- ✅ Statistics calculation (face vs image counts) - RESOLVED

### 11.6 Development Workflow 📋

**Running the Dashboard:**
```bash
# Development mode with auto-reload
phosor serve --reload

# Production mode
phosor serve --host 0.0.0.0 --port 8000

# Or directly with uvicorn
uvicorn frontend.app:app --reload
```

**Testing Approach:**
1. Unit tests for API endpoints (pytest + httpx)
2. Integration tests for file operations
3. Manual testing with browser
4. Optional: Playwright for E2E tests

**Deployment Considerations:**
- For local use: Just run `phosor serve`
- For network access: Use `--host 0.0.0.0`
- For production: Use reverse proxy (nginx) + systemd service
- Security: Add authentication if exposing to internet

### 11.7 Why This Architecture? 🤔

**Pros of FastAPI + Server-Side Rendering:**
- ✅ Fast development (no complex build pipeline)
- ✅ Leverages existing Python code directly
- ✅ Works with existing file structure
- ✅ Low resource usage (single Python process)
- ✅ Easy deployment (pip install + run)
- ✅ Auto-generated API docs (FastAPI feature)
- ✅ Type safety (Pydantic validation)

**Pros of Alpine.js over React/Vue:**
- ✅ No build step required
- ✅ Load from CDN (no npm/node_modules)
- ✅ Small footprint (~15KB)
- ✅ Easy to learn (HTML-first approach)
- ✅ Progressive enhancement ready
- ✅ Perfect for MVP scope

**Alternative Considered (NOT chosen for MVP):**
- ❌ React + Vite: Requires build pipeline, more complexity
- ❌ Next.js: Overkill for simple dashboard
- ❌ Django: Too heavyweight, we already have FastAPI
- ❌ Streamlit: Limited customization, not suitable for production

### 11.8 Implementation Priority 📋

**Phase 1 (Core MVP):** ✅ COMPLETED
1. ✅ FastAPI setup with basic structure
2. ✅ API endpoints for reading clusters
3. ✅ Dashboard home page (cluster grid)
4. ✅ Image serving endpoint
5. ✅ Basic styling with Tailwind

**Phase 2 (Essential Features):** ✅ COMPLETED
1. ✅ Cluster detail page
2. ✅ Image gallery with lightbox
3. ✅ Label editing functionality
4. ✅ Statistics display

**Phase 3 (Nice-to-Have):** 🔨 IN PROGRESS
1. 🔨 Cluster merging (API done, UI pending)
2. 📋 Filtering and sorting
3. ✅ Responsive design polish
4. ✅ Error handling and loading states

**Phase 4 (Advanced):** 📋 PLANNED
1. Real-time updates (WebSocket)
2. Face search functionality
3. Quality metrics
4. Export/sharing features

**Critical Bugs Fixed:**
1. ✅ **Route Ordering Issue** (11/2024)
   - Problem: Representative images returning 404
   - Root Cause: FastAPI matches routes sequentially; generic route `/{cluster}/{filename}` was catching requests meant for `/representative/{cluster}`
   - Solution: Moved specific route BEFORE generic route in `images.py`

2. ✅ **JavaScript Syntax Errors** (11/2024)
   - Problem: Alpine.js object properties had indentation issues
   - Solution: Fixed formatting in `cluster_detail.html`

3. ✅ **Non-Sequential Cluster Numbering** (12/2024)
   - Problem: Person_01, Person_02...Person_10, Person_12 (gaps due to filtered clusters)
   - Root Cause: Sequential labeling happened BEFORE filtering by `min_faces_per_cluster`
   - Solution: Applied sequential labeling AFTER filtering in `cli.py` (lines 123-129)

4. ✅ **Incorrect Statistics Display** (12/2024)
   - Problem: Total Images showed 60 instead of actual count; "3 images" displayed for all clusters
   - Root Cause: Using `len(sample_images)` instead of counting actual files in folder
   - Solution: Modified `list_clusters()` and `get_cluster()` to count real files from filesystem

**Deployment Status:**
- ✅ Development server running: `phosor serve --reload`
- ✅ Tested with real dataset: 78 images, 400 faces, 20 clusters
- ✅ All core features operational
- ✅ Responsive design verified on multiple screen sizes

---

## 12. Phase 2+ Hooks (Optional, Later)

The following are **future tasks**, the AI agent must not do them until MVP is stable:

1. Add support for **incremental update**:

   * Store image hashes and reuse embeddings.
2. Add **SQLite** metadata store (`phosor.db`).
3. Add **FastAPI** backend exposing:

   * Endpoint to list clusters.
   * Endpoint to merge/split clusters.
4. Add **simple web UI** to review faces and rename clusters.

---

## 12. Database Integration (Optional, Later)

The following are **future tasks**, for advanced features:

1. Add support for **incremental update**:

   * Store image hashes and reuse embeddings.
2. Add **SQLite** metadata store (`phosor.db`):
   * Migrate from JSON to SQLite for better querying
   * Store embeddings in database
   * Track scan history and changes
3. Add **PostgreSQL** support (if scaling beyond local use):
   * For multi-user scenarios
   * Better concurrent access

---

## 13. Single‑Paragraph Mission Brief for the Agent

> Implement Phosor as a Python CLI tool that scans a folder of photos, runs UniFace to detect faces and generate embeddings, clusters faces with DBSCAN, then copies/moves photos into per‑cluster folders and saves JSON metadata, following the stepwise tasks in this document. After the core CLI is stable, build an MVP web dashboard using FastAPI + server-side rendering (Jinja2) + Alpine.js for interactivity, allowing users to browse clusters, rename them, merge clusters, and view images through a clean web interface. Focus on rapid development without complex build tools—prioritize working features over perfect architecture.