"""Tests for folder manager module."""

import pytest
import tempfile
from pathlib import Path

from core.models import ClusterSummary, FaceRecord
from core.folder_manager import prepare_output_dirs, materialize_clusters


def test_prepare_output_dirs():
    """Test creating output directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        summaries = [
            ClusterSummary(cluster_id=0, label="Person_01", num_faces=5, sample_images=[]),
            ClusterSummary(cluster_id=1, label="Person_02", num_faces=3, sample_images=[]),
        ]
        
        cluster_paths = prepare_output_dirs(tmpdir, summaries, include_unclustered=True)
        
        assert len(cluster_paths) == 3  # 2 clusters + unclustered
        assert cluster_paths[0].endswith("Person_01")
        assert cluster_paths[1].endswith("Person_02")
        assert cluster_paths[-1].endswith("unclustered")
        
        # Verify folders exist
        assert Path(cluster_paths[0]).exists()
        assert Path(cluster_paths[1]).exists()
        assert Path(cluster_paths[-1]).exists()


def test_materialize_clusters_dry_run():
    """Test materialization in dry-run mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create source image
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()
        img_path = src_dir / "test.jpg"
        img_path.write_bytes(b"fake image data")
        
        # Create face record
        face = FaceRecord(
            id=1,
            image_path=str(img_path),
            face_index=0,
            bbox=(0, 0, 100, 100),
            embedding=[1.0] * 128,
            cluster_id=0,
        )
        
        summary = ClusterSummary(
            cluster_id=0,
            label="Person_01",
            num_faces=1,
            sample_images=[str(img_path)],
        )
        
        output_dir = Path(tmpdir) / "output"
        
        # Run dry-run
        materialize_clusters(
            [face], [summary], str(output_dir), mode="copy", dry_run=True
        )
        
        # Output should be created but image not copied
        assert output_dir.exists()
        person_dir = output_dir / "Person_01"
        assert person_dir.exists()
        assert not (person_dir / "test.jpg").exists()  # Not copied in dry-run
