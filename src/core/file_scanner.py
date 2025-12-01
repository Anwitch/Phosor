"""File scanning utilities for discovering image files."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def scan_images(
    input_dir: str, recursive: bool = True, min_file_size_kb: int = 50
) -> list[str]:
    """Scan directory for valid image files.

    Args:
        input_dir: Root directory to scan.
        recursive: Whether to scan subdirectories.
        min_file_size_kb: Minimum file size in KB to include.

    Returns:
        List of absolute paths to valid image files.
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return []

    image_paths: list[str] = []
    min_size_bytes = min_file_size_kb * 1024

    pattern = "**/*" if recursive else "*"
    for file_path in input_path.glob(pattern):
        if not file_path.is_file():
            continue

        # Check extension
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        # Check file size
        try:
            if file_path.stat().st_size < min_size_bytes:
                logger.debug(f"Skipping small file: {file_path}")
                continue
        except OSError as e:
            logger.warning(f"Error checking file {file_path}: {e}")
            continue

        image_paths.append(str(file_path.absolute()))

    logger.info(f"Found {len(image_paths)} valid images in {input_dir}")
    return image_paths
