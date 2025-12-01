"""Tests for FaceEngine module."""

import pytest
import numpy as np
import cv2

try:
    from core.face_engine import FaceEngine, UNIFACE_AVAILABLE
except ImportError:
    UNIFACE_AVAILABLE = False


@pytest.mark.skipif(not UNIFACE_AVAILABLE, reason="UniFace not installed")
class TestFaceEngine:
    """Tests for FaceEngine with UniFace."""

    def test_face_engine_initialization(self):
        """Test FaceEngine can be initialized."""
        engine = FaceEngine()
        assert engine is not None
        assert engine.detector is not None
        assert engine.recognizer is not None

    def test_detect_faces_empty_image(self):
        """Test detection with empty image."""
        engine = FaceEngine()
        
        # Empty array
        empty_image = np.array([])
        faces = engine.detect_faces(empty_image)
        assert faces == []
        
        # None image
        faces = engine.detect_faces(None)
        assert faces == []

    def test_detect_faces_no_faces(self):
        """Test detection on image without faces."""
        engine = FaceEngine()
        
        # Solid color image (no faces)
        blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = engine.detect_faces(blank_image)
        
        # Should return empty list or very low confidence detections
        assert isinstance(faces, list)

    def test_embed_face_without_landmarks(self):
        """Test embedding with missing landmarks."""
        engine = FaceEngine()
        
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        face_dict = {"bbox": (0, 0, 100, 100)}  # No landmarks
        
        embedding = engine.embed_face(image, face_dict)
        assert embedding is None

    def test_process_single_image_returns_list(self):
        """Test process_single_image returns proper format."""
        engine = FaceEngine()
        
        blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = engine.process_single_image(blank_image)
        
        assert isinstance(results, list)
        # With blank image, should be empty or contain face/embedding tuples
        for result in results:
            assert len(result) == 2  # (face_dict, embedding)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], np.ndarray)


def test_uniface_import():
    """Test that UniFace import status is tracked."""
    # This test always runs to verify the import guard works
    if UNIFACE_AVAILABLE:
        from core.face_engine import FaceEngine
        # Should be able to create instance
        engine = FaceEngine()
        assert engine is not None
    else:
        # Should raise ImportError when trying to initialize
        with pytest.raises(ImportError):
            from core.face_engine import FaceEngine
            FaceEngine()
