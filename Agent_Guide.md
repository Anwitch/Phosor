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

## 2. Config & Models Layer

**Goal:** Define data models & configuration handling before touching real logic.

### 2.1 Define Core Data Models

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

### 2.2 Implement Configuration Handling

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

### 2.3 Wire Config into CLI

Steps for the agent (in `src/core/cli.py`):

1. In `scan()`:

   * If `config` path is given → load config using `load_config`.
   * Override `input_dir` / `output_dir` if CLI args are provided.
2. Ensure `scan()` logs final resolved settings (input, output, clustering mode, etc.).

---

## 3. File Scanner Implementation

**Goal:** Turn a directory into a clean list of valid image paths.

### 3.1 Implement File Scanner

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

### 3.2 Integrate Scanner into CLI

Steps for the agent (in `src/core/cli.py`):

1. In `scan()`:

   * Call `scan_images(config.input.dir, config.input.recursive, config.input.min_file_size_kb)`.
   * Log number of discovered images.

---

## 4. Face Engine Wrapper (UniFace)

**Goal:** Wrap UniFace to provide a simple API: detect faces and get embeddings.

### 4.1 Implement FaceEngine Class

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

### 4.2 Implement Single‑Image Processing Helper

Steps for the agent (in `src/core/face_engine.py` or `src/core/utils.py`):

1. Implement function `process_image(image_path: str, engine: FaceEngine) -> list[FaceRecord]`:

   * Load image using `cv2.imread`.
   * Run `engine.detect_faces`.
   * For each detected face, compute embedding.
   * Return list of `FaceRecord` instances.
2. If `cv2.imread` returns `None`, log error and return empty list.

---

## 5. Embedding Collection Pipeline

**Goal:** For a batch of image paths, produce a list of FaceRecord objects.

### 5.1 Implement Batch Processing

Steps for the agent (new module or `utils.py`):

1. Implement function:

   ```python
   def build_face_dataset(image_paths: list[str], engine: FaceEngine) -> list[FaceRecord]:
       """Process all images and return list of FaceRecord with embeddings."""
   ```
2. Use `tqdm` progress bar around loop over images.
3. Aggregate all `FaceRecord` from all images into one list.
4. Assign incremental IDs to faces.

### 5.2 Add Minimal Tests

Steps for the agent:

1. Write a small unit/integration test that mocks `FaceEngine` methods to avoid real heavy model loading.
2. Ensure the function correctly flattens multiple images & faces into a single list of `FaceRecord`.

---

## 6. Clustering Logic

**Goal:** Cluster embeddings into groups using DBSCAN by default.

### 6.1 Implement Clustering Engine

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

### 6.2 Cluster Summary Builder

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

## 7. Output Writer (Folders + Metadata)

**Goal:** Take clustered data and materialize it into folder structure and JSON files.

### 7.1 Folder Manager

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

### 7.2 Copy / Move Files According to Cluster

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

### 7.3 Save Metadata JSON

Steps for the agent (in `src/core/utils.py` or dedicated module):

1. Implement function to save:

   * Full list of faces with embeddings & cluster ids → `embeddings.json`.
   * Cluster summaries → `clusters_summary.json`.
2. Use standard `json` module.
3. Make sure data is serializable (convert numpy arrays to lists).

---

## 8. Wiring Full Pipeline in CLI `scan`

**Goal:** Connect all core components into a working `phosor scan` command.

### 8.1 Implement Full Flow

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

## 9. `summary` Command Implementation

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

## 10. Basic Tests & Tooling

**Goal:** Ensure project doesn’t rot immediately.

### 10.1 Minimal Test Suite

Steps for the agent:

1. Add tests for:

   * `scan_images` behavior.
   * Clustering function with synthetic embeddings.
   * Folder manager (use temporary directories).
2. Configure `pytest` in `pyproject.toml` or `pytest.ini`.

### 10.2 Formatting & Linting

Steps for the agent:

1. Configure `black` & `ruff` in `pyproject.toml`.
2. Ensure code passes format + lint.

---

## 11. Phase 2+ Hooks (Optional, Later)

The following are **future tasks**, the AI agent must not do them until MVP is stable:

1. Add support for **incremental update**:

   * Store image hashes and reuse embeddings.
2. Add **SQLite** metadata store (`phosor.db`).
3. Add **FastAPI** backend exposing:

   * Endpoint to list clusters.
   * Endpoint to merge/split clusters.
4. Add **simple web UI** to review faces and rename clusters.

---

## 12. Single‑Paragraph Mission Brief for the Agent

> Implement Phosor as a Python CLI tool that scans a folder of photos, runs UniFace to detect faces and generate embeddings, clusters faces with DBSCAN, then copies/moves photos into per‑cluster folders and saves JSON metadata, following the stepwise tasks in this document. Focus on a clean, working MVP pipeline first (scan → embed → cluster → output) before touching any optional features such as DB, incremental update, or web dashboard.