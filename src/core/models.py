"""Data models for Phosor."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ImageRecord(BaseModel):
    """Represents a single image file."""

    id: int
    image_path: str
    hash: Optional[str] = None


class FaceRecord(BaseModel):
    """Represents a detected face with embedding."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    image_path: str
    face_index: int
    bbox: tuple[int, int, int, int]
    embedding: list[float]
    cluster_id: Optional[int] = None


class ClusterSummary(BaseModel):
    """Summary information for a face cluster."""

    cluster_id: int
    label: str
    num_faces: int
    sample_images: list[str] = Field(default_factory=list)
