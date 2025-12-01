"""API endpoints for image serving."""

import logging
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class MoveImageRequest(BaseModel):
    """Request model for moving image from unclustered to cluster."""
    filename: str
    target_cluster_id: int


class MoveImageMultipleRequest(BaseModel):
    """Request model for copying image to multiple clusters."""
    filename: str
    target_cluster_ids: list[int]
    create_new_cluster: Optional[str] = None


def get_output_dir() -> Path:
    """Get output directory from app state."""
    from frontend.app import state
    
    if not state.output_dir or not state.output_dir.exists():
        raise HTTPException(
            status_code=500,
            detail="Output directory not configured or does not exist"
        )
    return state.output_dir


@router.get("/images/representative/{cluster_label}")
async def serve_representative(cluster_label: str):
    """Serve the representative image for a cluster."""
    try:
        output_dir = get_output_dir()
        repr_path = output_dir / cluster_label / "_representative.jpg"
        
        logger.info(f"Looking for representative: {repr_path}")
        logger.info(f"File exists: {repr_path.exists()}")
        
        # If representative doesn't exist, try to use first image in folder as fallback
        if not repr_path.exists():
            logger.warning(f"Representative not found at {repr_path}, trying fallback...")
            cluster_folder = output_dir / cluster_label
            if cluster_folder.exists() and cluster_folder.is_dir():
                # Get first image file (not _representative.jpg)
                for img in cluster_folder.glob("*"):
                    if img.is_file() and img.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                        logger.info(f"Using fallback image: {img}")
                        repr_path = img
                        break
            
            if not repr_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"No images found for cluster: {cluster_label}"
                )
        
        # Security check: ensure path is within output directory
        try:
            repr_path.resolve().relative_to(output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Serving representative: {repr_path}")
        return FileResponse(
            path=str(repr_path),  # Convert Path to string
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400, immutable",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving representative for {cluster_label}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{cluster_label}/{filename}")
async def serve_image(cluster_label: str, filename: str):
    """Serve an image file from a cluster folder."""
    try:
        output_dir = get_output_dir()
        image_path = output_dir / cluster_label / filename
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
        
        if not image_path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {filename}")
        
        # Security check: ensure path is within output directory
        try:
            image_path.resolve().relative_to(output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FileResponse(
            path=image_path,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400, immutable",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image {cluster_label}/{filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/unclustered/{filename}")
async def serve_unclustered_image(filename: str):
    """Serve an image file from unclustered folder."""
    try:
        output_dir = get_output_dir()
        image_path = output_dir / "unclustered" / filename
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
        
        if not image_path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {filename}")
        
        # Security check: ensure path is within output directory
        try:
            image_path.resolve().relative_to(output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FileResponse(
            path=image_path,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400, immutable",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving unclustered image {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/move")
async def move_image_to_cluster(request: MoveImageRequest):
    """Move an image from unclustered folder to a cluster folder."""
    try:
        import json
        
        output_dir = get_output_dir()
        
        # Load clusters summary to get target cluster label
        summary_file = output_dir / "clusters_summary.json"
        if not summary_file.exists():
            raise HTTPException(status_code=404, detail="Clusters summary not found")
        
        with open(summary_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            clusters = data.get("clusters", data) if isinstance(data, dict) else data
        
        # Find target cluster
        target_cluster = next((c for c in clusters if c["cluster_id"] == request.target_cluster_id), None)
        if not target_cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {request.target_cluster_id} not found")
        
        # Source and destination paths
        source_path = output_dir / "unclustered" / request.filename
        target_folder = output_dir / target_cluster["label"]
        dest_path = target_folder / request.filename
        
        if not source_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {request.filename}")
        
        if not target_folder.exists():
            target_folder.mkdir(parents=True, exist_ok=True)
        
        # Handle filename conflicts
        counter = 1
        while dest_path.exists():
            stem = source_path.stem
            suffix = source_path.suffix
            dest_path = target_folder / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Copy (not move) the file
        shutil.copy2(str(source_path), str(dest_path))
        logger.info(f"Copied {request.filename} to cluster {target_cluster['label']}")
        
        # Update cluster summary (increment num_images)
        target_cluster["num_images"] = target_cluster.get("num_images", 0) + 1
        
        # Save updated summary
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({"clusters": clusters}, f, indent=2)
        
        return {
            "success": True,
            "filename": dest_path.name,
            "cluster_label": target_cluster["label"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving image {request.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/move-multiple")
async def move_image_to_multiple_clusters(request: MoveImageMultipleRequest):
    """Copy an image from unclustered folder to multiple clusters."""
    try:
        import json
        
        output_dir = get_output_dir()
        
        # Load clusters summary
        summary_file = output_dir / "clusters_summary.json"
        if not summary_file.exists():
            raise HTTPException(status_code=404, detail="Clusters summary not found")
        
        with open(summary_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            clusters = data.get("clusters", data) if isinstance(data, dict) else data
        
        # Source path
        source_path = output_dir / "unclustered" / request.filename
        if not source_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {request.filename}")
        
        copied_to = []
        
        # Create new cluster if requested
        if request.create_new_cluster:
            # Validate label
            if any(c["label"] == request.create_new_cluster for c in clusters):
                raise HTTPException(status_code=400, detail=f"Cluster '{request.create_new_cluster}' already exists")
            
            # Find highest cluster_id and increment
            max_cluster_id = max([c["cluster_id"] for c in clusters], default=-1)
            new_cluster_id = max_cluster_id + 1
            
            # Create folder
            new_folder = output_dir / request.create_new_cluster
            new_folder.mkdir(exist_ok=True)
            
            # Copy image to new cluster
            dest_path = new_folder / request.filename
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = new_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.copy2(str(source_path), str(dest_path))
            
            # Add to clusters list
            new_cluster = {
                "cluster_id": new_cluster_id,
                "label": request.create_new_cluster,
                "num_faces": 0,
                "sample_images": [request.filename],
            }
            clusters.append(new_cluster)
            copied_to.append(request.create_new_cluster)
            
            logger.info(f"Created new cluster '{request.create_new_cluster}' and copied {request.filename}")
        
        # Copy to existing clusters
        for cluster_id in request.target_cluster_ids:
            target_cluster = next((c for c in clusters if c["cluster_id"] == cluster_id), None)
            if not target_cluster:
                logger.warning(f"Cluster {cluster_id} not found, skipping")
                continue
            
            target_folder = output_dir / target_cluster["label"]
            if not target_folder.exists():
                target_folder.mkdir(parents=True, exist_ok=True)
            
            dest_path = target_folder / request.filename
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.copy2(str(source_path), str(dest_path))
            copied_to.append(target_cluster["label"])
            
            logger.info(f"Copied {request.filename} to cluster {target_cluster['label']}")
        
        # Save updated summary
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({"clusters": clusters}, f, indent=2)
        
        return {
            "success": True,
            "filename": request.filename,
            "copied_to": copied_to,
            "count": len(copied_to),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error copying image to multiple clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/images/{cluster_id}/{filename}")
async def delete_image_from_cluster(cluster_id: int, filename: str):
    """Delete an image from a cluster folder."""
    try:
        import json
        
        output_dir = get_output_dir()
        
        # Load clusters summary to get cluster label
        summary_file = output_dir / "clusters_summary.json"
        if not summary_file.exists():
            raise HTTPException(status_code=404, detail="Clusters summary not found")
        
        with open(summary_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            clusters = data.get("clusters", data) if isinstance(data, dict) else data
        
        # Find cluster
        cluster = next((c for c in clusters if c["cluster_id"] == cluster_id), None)
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        
        # Get image path
        image_path = output_dir / cluster["label"] / filename
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
        
        if not image_path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {filename}")
        
        # Security check: ensure path is within output directory
        try:
            image_path.resolve().relative_to(output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the file
        image_path.unlink()
        logger.info(f"Deleted image {filename} from cluster {cluster['label']}")
        
        # Update cluster summary (decrement num_faces)
        if cluster.get("num_faces", 0) > 0:
            cluster["num_faces"] -= 1
        
        # Save updated summary
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({"clusters": clusters}, f, indent=2)
        
        return {
            "success": True,
            "message": f"Image {filename} deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
