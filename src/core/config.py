"""Configuration handling for Phosor."""

import sys
from pathlib import Path
from typing import Optional, Literal

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from pydantic import BaseModel, Field


class InputConfig(BaseModel):
    """Input directory configuration."""

    dir: str
    recursive: bool = True
    min_file_size_kb: int = 50


class OutputConfig(BaseModel):
    """Output directory configuration."""

    dir: str
    mode: Literal["copy", "move"] = "copy"


class ClusteringConfig(BaseModel):
    """Clustering algorithm configuration."""

    method: Literal["dbscan", "kmeans"] = "dbscan"
    eps: float = 0.5
    min_samples: int = 3
    min_faces_per_cluster: int = 5


class HandlingConfig(BaseModel):
    """File handling configuration."""

    include_no_face: bool = False
    save_embeddings: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    file: str = "logs/phosor.log"


class PhosorConfig(BaseModel):
    """Main Phosor configuration."""

    input: InputConfig
    output: OutputConfig
    clustering: ClusteringConfig = Field(default_factory=ClusteringConfig)
    handling: HandlingConfig = Field(default_factory=HandlingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(path: Optional[str] = None) -> PhosorConfig:
    """Load configuration from TOML file or use defaults.

    Args:
        path: Optional path to config TOML file.

    Returns:
        PhosorConfig instance with loaded or default settings.
    """
    if path:
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(config_path, "rb") as f:
            config_dict = tomllib.load(f)
        return PhosorConfig(**config_dict)

    # Return default config
    return PhosorConfig(
        input=InputConfig(dir="data/input"),
        output=OutputConfig(dir="data/output"),
    )
