"""Face detection and embedding engine using UniFace."""

import logging
from typing import Optional
import numpy as np

try:
    from uniface import RetinaFace, ArcFace
    UNIFACE_AVAILABLE = True
except ImportError:
    UNIFACE_AVAILABLE = False

logger = logging.getLogger(__name__)


class FaceEngine:
    """Wrapper for UniFace face detection and embedding.
    
    Uses RetinaFace for face detection and ArcFace for face recognition.
    Models are automatically downloaded on first use.
    """

    def __init__(
        self,
        detector_conf_thresh: float = 0.5,
        detector_nms_thresh: float = 0.4,
    ):
        """Initialize UniFace models.
        
        Args:
            detector_conf_thresh: Confidence threshold for face detection.
            detector_nms_thresh: NMS threshold for face detection.
            
        Raises:
            ImportError: If UniFace is not installed.
            RuntimeError: If model initialization fails.
        """
        if not UNIFACE_AVAILABLE:
            raise ImportError(
                "UniFace is not installed. Install it with: pip install uniface"
            )
        
        try:
            logger.info("Initializing UniFace models...")
            
            # Initialize RetinaFace detector (mnet_v2 - balanced accuracy/speed)
            self.detector = RetinaFace(
                conf_thresh=detector_conf_thresh,
                nms_thresh=detector_nms_thresh,
            )
            logger.info("RetinaFace detector initialized")
            
            # Initialize ArcFace recognizer
            self.recognizer = ArcFace()
            logger.info("ArcFace recognizer initialized")
            
            logger.info("FaceEngine ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize FaceEngine: {e}")
            raise RuntimeError(f"FaceEngine initialization failed: {e}")

    def detect_faces(self, image: np.ndarray) -> list[dict]:
        """Detect faces in an image using RetinaFace.

        Args:
            image: Input image as numpy array (BGR format from cv2).

        Returns:
            List of face detections. Each dict contains:
                - bbox: tuple of (x1, y1, x2, y2)
                - confidence: detection confidence score
                - landmarks: 5-point facial landmarks (eyes, nose, mouth corners)
                  as list of (x, y) tuples
        """
        if image is None or image.size == 0:
            logger.warning("Empty or invalid image provided")
            return []
        
        try:
            # UniFace detect returns list of dicts with bbox, confidence, landmarks
            detections = self.detector.detect(image)
            
            if not detections:
                logger.debug("No faces detected in image")
                return []
            
            logger.debug(f"Detected {len(detections)} face(s)")
            
            # Ensure consistent format
            formatted_detections = []
            for detection in detections:
                formatted = {
                    'bbox': tuple(map(int, detection['bbox'])),  # (x1, y1, x2, y2)
                    'confidence': float(detection['confidence']),
                    'landmarks': detection['landmarks'],  # 5-point landmarks
                }
                formatted_detections.append(formatted)
            
            return formatted_detections
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []

    def embed_face(self, image: np.ndarray, face: dict) -> Optional[np.ndarray]:
        """Extract normalized face embedding vector using ArcFace.

        Args:
            image: Input image as numpy array (BGR format).
            face: Face detection dict with 'landmarks' key.

        Returns:
            Normalized embedding vector as numpy array (512-dim),
            or None if extraction fails.
        """
        if image is None or image.size == 0:
            logger.warning("Empty or invalid image for embedding")
            return None
        
        if 'landmarks' not in face:
            logger.warning("Face dict missing 'landmarks' key")
            return None
        
        try:
            # ArcFace.get_normalized_embedding returns normalized 512-dim vector
            embedding = self.recognizer.get_normalized_embedding(
                image, face['landmarks']
            )
            
            if embedding is None:
                logger.warning("Embedding extraction returned None")
                return None
            
            # Ensure it's a 1D array
            if len(embedding.shape) == 2:
                embedding = embedding.flatten()
            
            logger.debug(f"Extracted embedding with shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Face embedding failed: {e}")
            return None
    
    def process_single_image(self, image: np.ndarray) -> list[tuple[dict, np.ndarray]]:
        """Detect faces and extract embeddings from a single image.
        
        Convenience method that combines detection and embedding extraction.
        
        Args:
            image: Input image as numpy array (BGR format).
            
        Returns:
            List of (face_dict, embedding) tuples. Face dict contains
            bbox, confidence, and landmarks.
        """
        results = []
        
        # Detect faces
        faces = self.detect_faces(image)
        
        if not faces:
            return results
        
        # Extract embeddings for each face
        for face in faces:
            embedding = self.embed_face(image, face)
            if embedding is not None:
                results.append((face, embedding))
            else:
                logger.warning(f"Skipping face due to embedding failure")
        
        return results
