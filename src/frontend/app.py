"""FastAPI application for Phosor Web Dashboard."""

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config import load_config, PhosorConfig
from frontend.api import clusters, images

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Phosor Dashboard",
    description="Web interface for Photo Sorting Orchestrator",
    version="1.0.0",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Mount static files
static_dir = PROJECT_ROOT / "src" / "frontend" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Setup Jinja2 templates
templates_dir = PROJECT_ROOT / "src" / "frontend" / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Application state
class AppState:
    """Global application state."""
    
    config: Optional[PhosorConfig] = None
    output_dir: Optional[Path] = None

state = AppState()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Load Phosor configuration
        config_path = PROJECT_ROOT / "configs" / "config.toml"
        if config_path.exists():
            state.config = load_config(str(config_path))
            state.output_dir = Path(state.config.output.dir)
            logger.info(f"Loaded config from {config_path}")
            logger.info(f"Output directory: {state.output_dir}")
        else:
            logger.warning(f"Config not found at {config_path}, using defaults")
            state.config = load_config()
            state.output_dir = Path(state.config.output.dir)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        # Use default config as fallback
        state.config = load_config()
        state.output_dir = Path(state.config.output.dir)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard home page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Phosor Dashboard",
            "output_dir": str(state.output_dir) if state.output_dir else "Not configured",
        }
    )


@app.get("/cluster/{cluster_id}", response_class=HTMLResponse)
async def cluster_detail(request: Request, cluster_id: int):
    """Cluster detail page."""
    # Load cluster data
    from frontend.api.clusters import load_clusters_summary
    
    try:
        clusters_data = load_clusters_summary()
        cluster = next((c for c in clusters_data if c["cluster_id"] == cluster_id), None)
        
        if not cluster:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": f"Cluster {cluster_id} not found"
            }, status_code=404)
        
        return templates.TemplateResponse("cluster_detail.html", {
            "request": request,
            "cluster": cluster,
        })
    except Exception as e:
        logger.error(f"Error loading cluster {cluster_id}: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": str(e)
        }, status_code=500)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "config_loaded": state.config is not None,
        "output_dir": str(state.output_dir) if state.output_dir else None,
    }


# Include API routers
app.include_router(clusters.router, prefix="/api", tags=["clusters"])
app.include_router(images.router, prefix="/api", tags=["images"])

logger.info("Phosor Dashboard initialized")
