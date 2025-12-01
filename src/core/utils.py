"""Utility functions for Phosor."""

import json
import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from tqdm import tqdm

from core.models import FaceRecord, ClusterSummary
from core.face_engine import FaceEngine

logger = logging.getLogger(__name__)


def process_image(image_path: str, engine: FaceEngine) -> list[FaceRecord]:
    """Process a single image to extract face records.

    Args:
        image_path: Path to image file.
        engine: FaceEngine instance.

    Returns:
        List of FaceRecord for detected faces.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Failed to load image: {image_path}")
        return []

    # Detect faces and extract embeddings
    results = engine.process_single_image(image)
    
    if not results:
        logger.debug(f"No faces detected or embedded in {image_path}")
        return []

    # Convert to FaceRecord
    face_records = []
    for idx, (face_dict, embedding) in enumerate(results):
        bbox = face_dict.get("bbox", (0, 0, 0, 0))
        
        face_record = FaceRecord(
            id=0,  # Will be assigned later
            image_path=image_path,
            face_index=idx,
            bbox=bbox,
            embedding=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
        )
        face_records.append(face_record)
    
    logger.debug(f"Extracted {len(face_records)} face(s) from {image_path}")
    return face_records


def build_face_dataset(
    image_paths: list[str], engine: FaceEngine
) -> list[FaceRecord]:
    """Process batch of images to build face dataset.

    Args:
        image_paths: List of image file paths.
        engine: FaceEngine instance.

    Returns:
        List of all FaceRecord from all images.
    """
    all_faces = []
    face_id = 1

    logger.info(f"Processing {len(image_paths)} images...")
    
    for image_path in tqdm(image_paths, desc="Extracting faces"):
        faces = process_image(image_path, engine)
        
        # Assign incremental IDs
        for face in faces:
            face.id = face_id
            face_id += 1
        
        all_faces.extend(faces)

    logger.info(f"Extracted {len(all_faces)} faces from {len(image_paths)} images")
    return all_faces


def save_embeddings(faces: list[FaceRecord], output_path: str) -> None:
    """Save face embeddings to JSON file.

    Args:
        faces: List of FaceRecord.
        output_path: Path to output JSON file.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to serializable format
    data = [face.model_dump() for face in faces]

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved {len(faces)} face embeddings to {output_path}")


def save_cluster_summary(summaries: list[ClusterSummary], output_path: str) -> None:
    """Save cluster summaries to JSON file.

    Args:
        summaries: List of ClusterSummary.
        output_path: Path to output JSON file.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to serializable format
    data = {
        "clusters": [summary.model_dump() for summary in summaries],
        "total_clusters": len(summaries),
    }

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved {len(summaries)} cluster summaries to {output_path}")
