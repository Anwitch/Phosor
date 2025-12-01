"""Configuration handling for Phosor."""

import sys
import re
from pathlib import Path
from typing import Optional, Literal

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from pydantic import BaseModel, Field, field_validator


class InputConfig(BaseModel):
    """Input directory configuration."""

    dir: str
    recursive: bool = True
    min_file_size_kb: int = 50
    
    @field_validator('dir')
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Normalize Windows/Unix paths and handle raw strings."""
        # Convert single backslashes to forward slashes for consistency
        # This allows users to use C:\path or C:\\path in TOML
        return str(Path(v).as_posix())


class OutputConfig(BaseModel):
    """Output directory configuration."""

    dir: str
    mode: Literal["copy", "move"] = "copy"
    create_representatives: bool = True
    representative_mode: Literal["crop", "bbox", "annotated"] = "crop"
    
    @field_validator('dir')
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Normalize Windows/Unix paths and handle raw strings."""
        return str(Path(v).as_posix())


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
    
    @field_validator('file')
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Normalize Windows/Unix paths and handle raw strings."""
        return str(Path(v).as_posix())


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

        # Read and preprocess TOML to handle Windows paths
        with open(config_path, "r", encoding="utf-8") as f:
            toml_content = f.read()
        
        # Replace single backslashes with double backslashes in path values
        # This handles Windows paths like C:\Users -> C:\\Users
        import re
        def fix_windows_path(match):
            path_value = match.group(1)
            # Replace single backslashes with double backslashes
            fixed_path = path_value.replace('\\', '\\\\')
            return f'"{fixed_path}"'
        
        # Match quoted strings that look like Windows paths (contain :\ or starts with \)
        toml_content = re.sub(r'"([A-Za-z]:[^"]*)"', fix_windows_path, toml_content)
        
        # Parse the preprocessed TOML
        config_dict = tomllib.loads(toml_content)
        return PhosorConfig(**config_dict)

    # Return default config
    return PhosorConfig(
        input=InputConfig(dir="data/input"),
        output=OutputConfig(dir="data/output"),
    )
