"""Tests for file scanner module."""

import pytest
from pathlib import Path
import tempfile
import shutil

from core.file_scanner import scan_images


def test_scan_images_empty_dir():
    """Test scanning an empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scan_images(tmpdir)
        assert result == []


def test_scan_images_with_valid_files():
    """Test scanning directory with valid image files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files
        (tmppath / "test1.jpg").write_bytes(b"x" * 60000)  # 60KB
        (tmppath / "test2.png").write_bytes(b"x" * 60000)
        (tmppath / "test3.txt").write_bytes(b"x" * 60000)  # Should be ignored
        
        result = scan_images(tmpdir, min_file_size_kb=50)
        
        assert len(result) == 2
        assert any("test1.jpg" in p for p in result)
        assert any("test2.png" in p for p in result)


def test_scan_images_filters_small_files():
    """Test that small files are filtered out."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create small file
        (tmppath / "small.jpg").write_bytes(b"x" * 1000)  # 1KB
        
        result = scan_images(tmpdir, min_file_size_kb=50)
        
        assert len(result) == 0


def test_scan_images_recursive():
    """Test recursive scanning of subdirectories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create nested structure
        subdir = tmppath / "subdir"
        subdir.mkdir()
        
        (tmppath / "root.jpg").write_bytes(b"x" * 60000)
        (subdir / "nested.jpg").write_bytes(b"x" * 60000)
        
        # Recursive scan
        result = scan_images(tmpdir, recursive=True, min_file_size_kb=50)
        assert len(result) == 2
        
        # Non-recursive scan
        result = scan_images(tmpdir, recursive=False, min_file_size_kb=50)
        assert len(result) == 1
