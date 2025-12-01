"""Tests for clustering module."""

import pytest
import numpy as np

from core.models import FaceRecord, ClusterSummary
from core.clustering import cluster_faces, build_cluster_summary


def create_mock_face(face_id: int, embedding: list[float], image_path: str = "test.jpg") -> FaceRecord:
    """Helper to create mock FaceRecord."""
    return FaceRecord(
        id=face_id,
        image_path=image_path,
        face_index=0,
        bbox=(0, 0, 100, 100),
        embedding=embedding,
    )


def test_cluster_faces_empty_list():
    """Test clustering with empty face list."""
    result = cluster_faces([])
    assert result == []


def test_cluster_faces_dbscan():
    """Test DBSCAN clustering with synthetic embeddings."""
    # Create two distinct groups
    faces = []
    
    # Group 1: similar embeddings
    for i in range(5):
        emb = [1.0 + i * 0.01] * 128
        faces.append(create_mock_face(i, emb, f"img{i}.jpg"))
    
    # Group 2: different embeddings
    for i in range(5, 10):
        emb = [5.0 + (i-5) * 0.01] * 128
        faces.append(create_mock_face(i, emb, f"img{i}.jpg"))
    
    result = cluster_faces(faces, method="dbscan", eps=0.3, min_samples=2)
    
    # Check that cluster IDs are assigned
    for face in result:
        assert face.cluster_id is not None


def test_build_cluster_summary():
    """Test building cluster summary from faces."""
    faces = []
    
    # Create faces in 2 clusters
    for i in range(3):
        face = create_mock_face(i, [1.0] * 128, f"img{i}.jpg")
        face.cluster_id = 0
        faces.append(face)
    
    for i in range(3, 6):
        face = create_mock_face(i, [2.0] * 128, f"img{i}.jpg")
        face.cluster_id = 1
        faces.append(face)
    
    summaries = build_cluster_summary(faces)
    
    assert len(summaries) == 2
    assert summaries[0].cluster_id == 0
    assert summaries[0].num_faces == 3
    assert summaries[0].label == "Person_01"
    assert summaries[1].cluster_id == 1
    assert summaries[1].num_faces == 3
    assert summaries[1].label == "Person_02"


def test_build_cluster_summary_ignores_noise():
    """Test that noise cluster (-1) is ignored in summary."""
    faces = []
    
    # Valid cluster
    face1 = create_mock_face(1, [1.0] * 128, "img1.jpg")
    face1.cluster_id = 0
    faces.append(face1)
    
    # Noise
    face2 = create_mock_face(2, [2.0] * 128, "img2.jpg")
    face2.cluster_id = -1
    faces.append(face2)
    
    summaries = build_cluster_summary(faces)
    
    assert len(summaries) == 1
    assert summaries[0].cluster_id == 0
