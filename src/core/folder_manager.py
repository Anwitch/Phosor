"""Folder and file management for output organization."""

import logging
import shutil
from pathlib import Path
from collections import defaultdict

import cv2
import numpy as np

from core.models import ClusterSummary, FaceRecord

logger = logging.getLogger(__name__)


def prepare_output_dirs(
    base_output_dir: str,
    clusters: list[ClusterSummary],
    include_unclustered: bool = True,
) -> dict[int, str]:
    """Create output directory structure for clusters.

    Args:
        base_output_dir: Base output directory path.
        clusters: List of cluster summaries.
        include_unclustered: Whether to create unclustered folder.

    Returns:
        Mapping of cluster_id to folder path.
    """
    output_path = Path(base_output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cluster_paths = {}

    # Create folder for each cluster
    for cluster in clusters:
        folder_path = output_path / cluster.label
        folder_path.mkdir(exist_ok=True)
        cluster_paths[cluster.cluster_id] = str(folder_path)
        logger.debug(f"Created folder: {folder_path}")

    # Create unclustered folder
    if include_unclustered:
        unclustered_path = output_path / "unclustered"
        unclustered_path.mkdir(exist_ok=True)
        cluster_paths[-1] = str(unclustered_path)
        logger.debug(f"Created unclustered folder: {unclustered_path}")

    logger.info(f"Prepared {len(cluster_paths)} output folders")
    return cluster_paths


def materialize_clusters(
    faces: list[FaceRecord],
    cluster_summaries: list[ClusterSummary],
    output_dir: str,
    mode: str = "copy",
    dry_run: bool = False,
) -> None:
    """Copy or move images to cluster folders.

    Args:
        faces: List of FaceRecord with cluster assignments.
        cluster_summaries: List of cluster summaries.
        output_dir: Base output directory.
        mode: "copy" or "move".
        dry_run: If True, only log actions without executing.
    """
    # Prepare output directories
    cluster_paths = prepare_output_dirs(output_dir, cluster_summaries)

    # Group images by cluster
    cluster_images = defaultdict(set)
    for face in faces:
        if face.cluster_id is not None:
            cluster_images[face.cluster_id].add(face.image_path)

    # Process each cluster
    total_copied = 0
    for cluster_id, image_paths in cluster_images.items():
        if cluster_id not in cluster_paths:
            logger.warning(f"No folder for cluster {cluster_id}, skipping")
            continue

        dest_folder = Path(cluster_paths[cluster_id])

        for image_path in image_paths:
            src_path = Path(image_path)
            if not src_path.exists():
                logger.warning(f"Source file not found: {image_path}")
                continue

            dest_path = dest_folder / src_path.name

            # Handle name conflicts
            counter = 1
            while dest_path.exists():
                dest_path = dest_folder / f"{src_path.stem}_{counter}{src_path.suffix}"
                counter += 1

            if dry_run:
                logger.info(f"[DRY RUN] Would {mode} {src_path} -> {dest_path}")
            else:
                try:
                    if mode == "copy":
                        shutil.copy2(src_path, dest_path)
                    elif mode == "move":
                        shutil.move(str(src_path), dest_path)
                    else:
                        raise ValueError(f"Unknown mode: {mode}")
                    total_copied += 1
                except Exception as e:
                    logger.error(f"Failed to {mode} {src_path}: {e}")
    
    if not dry_run:
        logger.info(f"Successfully {mode}d {total_copied} images")
    else:
        logger.info(f"[DRY RUN] Would {mode} {total_copied} images")


def create_cluster_representatives(
    faces: list[FaceRecord],
    cluster_summaries: list[ClusterSummary],
    output_dir: str,
    mode: str = "crop",
    dry_run: bool = False,
) -> None:
    """Create representative face images for each cluster.
    
    Creates a visual reference showing which person each cluster represents.
    Saves as '_representative.jpg' in each cluster folder.
    
    Args:
        faces: List of FaceRecord with cluster assignments and bboxes.
        cluster_summaries: List of cluster summaries.
        output_dir: Base output directory.
        mode: How to create representative:
            - "crop": Crop just the face region (square)
            - "bbox": Draw bounding box on full image
            - "annotated": Full image with bbox and confidence
        dry_run: If True, only log actions without executing.
    """
    output_path = Path(output_dir)
    
    # Group faces by cluster
    cluster_faces = defaultdict(list)
    for face in faces:
        if face.cluster_id is not None and face.cluster_id >= 0:
            cluster_faces[face.cluster_id].append(face)
    
    created_count = 0
    
    for summary in cluster_summaries:
        cluster_id = summary.cluster_id
        cluster_label = summary.label
        
        if cluster_id not in cluster_faces:
            logger.warning(f"No faces found for cluster {cluster_id}")
            continue
        
        # Get the first face (usually highest confidence or first detected)
        representative_face = cluster_faces[cluster_id][0]
        
        # Load the source image
        image_path = representative_face.image_path
        image = cv2.imread(image_path)
        
        if image is None:
            logger.warning(f"Could not load image: {image_path}")
            continue
        
        # Get bounding box
        x1, y1, x2, y2 = representative_face.bbox
        
        # Create representative image based on mode
        if mode == "crop":
            # Crop the face region with some padding
            padding = 30
            h, w = image.shape[:2]
            
            # Add padding and ensure within image bounds
            x1_pad = max(0, x1 - padding)
            y1_pad = max(0, y1 - padding)
            x2_pad = min(w, x2 + padding)
            y2_pad = min(h, y2 + padding)
            
            # Crop the face
            face_crop = image[y1_pad:y2_pad, x1_pad:x2_pad]
            
            # Resize to standard size for consistency
            if face_crop.size > 0:
                target_size = 200
                face_crop = cv2.resize(face_crop, (target_size, target_size))
            
            output_image = face_crop
            
        elif mode == "bbox":
            # Draw bounding box on full image
            output_image = image.copy()
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            
        elif mode == "annotated":
            # Full image with bbox and label
            output_image = image.copy()
            
            # Draw bounding box
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            
            # Add label
            label_text = f"{cluster_label}"
            cv2.putText(
                output_image,
                label_text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )
        else:
            logger.warning(f"Unknown mode: {mode}, using crop")
            output_image = image[y1:y2, x1:x2]
        
        # Save representative image
        cluster_folder = output_path / cluster_label
        representative_path = cluster_folder / "_representative.jpg"
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create representative: {representative_path}")
        else:
            try:
                cv2.imwrite(str(representative_path), output_image)
                created_count += 1
                logger.debug(f"Created representative for {cluster_label}")
            except Exception as e:
                logger.error(f"Failed to create representative for {cluster_label}: {e}")
    
    if not dry_run:
        logger.info(f"Created {created_count} cluster representative images")
    else:
        logger.info(f"[DRY RUN] Would create {created_count} representative images")
