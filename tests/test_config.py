"""Tests for configuration module."""

import pytest
import tempfile
from pathlib import Path

from core.config import load_config, PhosorConfig


def test_load_config_defaults():
    """Test loading default configuration."""
    config = load_config()
    
    assert config.input.dir == "data/input"
    assert config.output.dir == "data/output"
    assert config.clustering.method == "dbscan"
    assert config.logging.level == "INFO"


def test_load_config_from_file():
    """Test loading configuration from TOML file."""
    toml_content = """
[input]
dir = "/custom/input"
recursive = false

[output]
dir = "/custom/output"
mode = "move"

[clustering]
method = "kmeans"
eps = 0.7
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(toml_content)
        config_path = f.name
    
    try:
        config = load_config(config_path)
        
        assert config.input.dir == "/custom/input"
        assert config.input.recursive is False
        assert config.output.dir == "/custom/output"
        assert config.output.mode == "move"
        assert config.clustering.method == "kmeans"
        assert config.clustering.eps == 0.7
    finally:
        Path(config_path).unlink()


def test_load_config_file_not_found():
    """Test that FileNotFoundError is raised for missing config."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/config.toml")
