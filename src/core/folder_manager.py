"""Folder and file management for output organization."""

import logging
import shutil
from pathlib import Path
from collections import defaultdict

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
                    logger.error(f"Error processing {src_path}: {e}")

    if not dry_run:
        logger.info(f"Successfully {mode}d {total_copied} images")
    else:
        logger.info(f"[DRY RUN] Would {mode} {total_copied} images")
