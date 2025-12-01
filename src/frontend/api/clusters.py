"""API endpoints for cluster management."""

import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ClusterInfo(BaseModel):
    """Cluster information model."""
    cluster_id: int
    label: str
    num_faces: int
    num_images: int
    sample_images: List[str] = []


class ClusterUpdateRequest(BaseModel):
    """Request model for updating cluster label."""
    label: str


class ClusterMergeRequest(BaseModel):
    """Request model for merging clusters."""
    source_ids: List[int]
    target_id: int


class CreateClusterRequest(BaseModel):
    """Request model for creating a new cluster."""
    label: str


class UnclusteredImage(BaseModel):
    """Unclustered image information."""
    filename: str
    path: str


def get_output_dir() -> Path:
    """Get output directory from app state."""
    from frontend.app import state
    
    if not state.output_dir or not state.output_dir.exists():
        raise HTTPException(
            status_code=500,
            detail="Output directory not configured or does not exist"
        )
    return state.output_dir


def load_clusters_summary() -> List[dict]:
    """Load clusters summary from JSON file."""
    output_dir = get_output_dir()
    summary_file = output_dir / "clusters_summary.json"
    
    if not summary_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Clusters summary not found at {summary_file}"
        )
    
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Handle both formats: {"clusters": [...]} or [...]
        if isinstance(data, dict) and "clusters" in data:
            return data["clusters"]
        return data
    except Exception as e:
        logger.error(f"Error loading clusters summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def save_clusters_summary(data: List[dict]) -> None:
    """Save clusters summary to JSON file."""
    output_dir = get_output_dir()
    summary_file = output_dir / "clusters_summary.json"
    
    try:
        # Maintain the wrapper format
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({"clusters": data}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving clusters summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters", response_model=List[ClusterInfo])
async def list_clusters():
    """List all clusters from clusters_summary.json."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Convert to ClusterInfo models
        clusters = []
        for cluster in clusters_data:
            # Count actual images in folder
            cluster_folder = output_dir / cluster["label"]
            num_images = 0
            if cluster_folder.exists():
                num_images = len([f for f in cluster_folder.glob("*") 
                                if f.is_file() and f.name != "_representative.jpg" 
                                and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
            
            clusters.append(ClusterInfo(
                cluster_id=cluster["cluster_id"],
                label=cluster["label"],
                num_faces=cluster["num_faces"],
                num_images=num_images,
                sample_images=cluster.get("sample_images", [])[:3],  # First 3 samples
            ))
        
        return clusters
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters/{cluster_id}", response_model=ClusterInfo)
async def get_cluster(cluster_id: int):
    """Get detailed information about a specific cluster."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Find cluster by ID
        cluster = next((c for c in clusters_data if c["cluster_id"] == cluster_id), None)
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        
        # Count actual images in folder
        cluster_folder = output_dir / cluster["label"]
        num_images = 0
        if cluster_folder.exists():
            num_images = len([f for f in cluster_folder.glob("*") 
                            if f.is_file() and f.name != "_representative.jpg" 
                            and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
        
        return ClusterInfo(
            cluster_id=cluster["cluster_id"],
            label=cluster["label"],
            num_faces=cluster["num_faces"],
            num_images=num_images,
            sample_images=cluster.get("sample_images", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cluster {cluster_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters/{cluster_id}/images")
async def get_cluster_images(cluster_id: int):
    """Get list of images in a cluster."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Find cluster
        cluster = next((c for c in clusters_data if c["cluster_id"] == cluster_id), None)
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        
        # Get cluster folder
        cluster_folder = output_dir / cluster["label"]
        if not cluster_folder.exists():
            raise HTTPException(status_code=404, detail=f"Cluster folder not found: {cluster['label']}")
        
        # List all images in folder (excluding _representative.jpg)
        images = []
        for img_path in cluster_folder.glob("*"):
            if img_path.is_file() and img_path.name != "_representative.jpg":
                if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                    images.append({
                        "filename": img_path.name,
                        "path": str(img_path),
                        "size": img_path.stat().st_size,
                    })
        
        return {
            "cluster_id": cluster_id,
            "label": cluster["label"],
            "images": images,
            "total": len(images),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting images for cluster {cluster_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/clusters/{cluster_id}")
async def update_cluster(cluster_id: int, request: ClusterUpdateRequest):
    """Update cluster label (rename)."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Find cluster
        cluster = next((c for c in clusters_data if c["cluster_id"] == cluster_id), None)
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        
        old_label = cluster["label"]
        new_label = request.label
        
        # Validate new label
        if not new_label or not new_label.strip():
            raise HTTPException(status_code=400, detail="Label cannot be empty")
        
        # Check if new label already exists
        if any(c["label"] == new_label for c in clusters_data if c["cluster_id"] != cluster_id):
            raise HTTPException(status_code=400, detail=f"Label '{new_label}' already exists")
        
        # Rename folder
        old_folder = output_dir / old_label
        new_folder = output_dir / new_label
        
        if old_folder.exists():
            old_folder.rename(new_folder)
            logger.info(f"Renamed folder: {old_label} -> {new_label}")
        
        # Update cluster data
        cluster["label"] = new_label
        
        # Save updated summary
        save_clusters_summary(clusters_data)
        
        return {
            "success": True,
            "cluster_id": cluster_id,
            "old_label": old_label,
            "new_label": new_label,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cluster {cluster_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clusters/merge")
async def merge_clusters(request: ClusterMergeRequest):
    """Merge multiple clusters into one."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Validate source and target clusters
        source_clusters = [c for c in clusters_data if c["cluster_id"] in request.source_ids]
        target_cluster = next((c for c in clusters_data if c["cluster_id"] == request.target_id), None)
        
        if not target_cluster:
            raise HTTPException(status_code=404, detail=f"Target cluster {request.target_id} not found")
        
        if len(source_clusters) != len(request.source_ids):
            raise HTTPException(status_code=404, detail="One or more source clusters not found")
        
        # Move images from source clusters to target
        target_folder = output_dir / target_cluster["label"]
        moved_count = 0
        
        for source_cluster in source_clusters:
            source_folder = output_dir / source_cluster["label"]
            
            if source_folder.exists():
                # Move all images
                for img_path in source_folder.glob("*"):
                    if img_path.is_file() and img_path.name != "_representative.jpg":
                        dest_path = target_folder / img_path.name
                        
                        # Replace if file exists with same name
                        if dest_path.exists():
                            dest_path.unlink()  # Delete existing file
                            logger.info(f"Replaced existing file: {dest_path.name}")
                        
                        shutil.move(str(img_path), str(dest_path))
                        moved_count += 1
                
                # Remove source folder
                shutil.rmtree(source_folder)
                logger.info(f"Merged and removed cluster: {source_cluster['label']}")
        
        # Update clusters summary (remove source clusters, update target)
        clusters_data = [c for c in clusters_data if c["cluster_id"] not in request.source_ids]
        
        # Update target cluster face count (approximate)
        target_in_data = next(c for c in clusters_data if c["cluster_id"] == request.target_id)
        for source in source_clusters:
            target_in_data["num_faces"] += source["num_faces"]
        
        save_clusters_summary(clusters_data)
        
        return {
            "success": True,
            "target_id": request.target_id,
            "merged_clusters": [c["cluster_id"] for c in source_clusters],
            "images_moved": moved_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error merging clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clusters")
async def create_cluster(request: CreateClusterRequest):
    """Create a new empty cluster."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Validate label
        if not request.label or not request.label.strip():
            raise HTTPException(status_code=400, detail="Label cannot be empty")
        
        # Check if label already exists
        if any(c["label"] == request.label for c in clusters_data):
            raise HTTPException(status_code=400, detail=f"Label '{request.label}' already exists")
        
        # Find highest cluster_id and increment
        max_cluster_id = max([c["cluster_id"] for c in clusters_data], default=-1)
        new_cluster_id = max_cluster_id + 1
        
        # Create new cluster folder
        cluster_folder = output_dir / request.label
        cluster_folder.mkdir(exist_ok=True)
        
        # Add to clusters summary
        new_cluster = {
            "cluster_id": new_cluster_id,
            "label": request.label,
            "num_faces": 0,
            "sample_images": [],
        }
        clusters_data.append(new_cluster)
        
        # Save updated summary
        save_clusters_summary(clusters_data)
        
        logger.info(f"Created new cluster: {request.label} (ID: {new_cluster_id})")
        
        return {
            "success": True,
            "cluster_id": new_cluster_id,
            "label": request.label,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating cluster: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unclustered", response_model=List[UnclusteredImage])
async def get_unclustered_images():
    """Get list of unclustered images."""
    try:
        output_dir = get_output_dir()
        unclustered_folder = output_dir / "unclustered"
        
        if not unclustered_folder.exists():
            return []
        
        images = []
        for img_path in unclustered_folder.glob("*"):
            if img_path.is_file() and img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                images.append(UnclusteredImage(
                    filename=img_path.name,
                    path=str(img_path),
                ))
        
        return images
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting unclustered images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clusters/{cluster_id}")
async def delete_cluster(cluster_id: int):
    """Delete a cluster and all its images."""
    try:
        output_dir = get_output_dir()
        clusters_data = load_clusters_summary()
        
        # Find cluster
        cluster = next((c for c in clusters_data if c["cluster_id"] == cluster_id), None)
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")
        
        # Delete cluster folder and all its contents
        cluster_folder = output_dir / cluster["label"]
        if cluster_folder.exists():
            shutil.rmtree(cluster_folder)
            logger.info(f"Deleted cluster folder: {cluster['label']}")
        
        # Remove from clusters summary
        clusters_data = [c for c in clusters_data if c["cluster_id"] != cluster_id]
        save_clusters_summary(clusters_data)
        
        return {
            "success": True,
            "cluster_id": cluster_id,
            "label": cluster["label"],
            "message": f"Cluster '{cluster['label']}' deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cluster {cluster_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
