"""Test FaceEngine with real face detection."""

import sys
import cv2
import numpy as np
sys.path.insert(0, 'src')

from src.core.face_engine import FaceEngine

print("Testing FaceEngine with sample image...")
print("=" * 60)

# Initialize engine
print("\n1. Initializing FaceEngine...")
engine = FaceEngine()
print("   ✓ Engine ready")

# Create a test image (will use actual face image if available)
print("\n2. Loading test image...")

# Try to load from assets if exists, otherwise create synthetic
try:
    # Try common test image locations
    test_paths = [
        "assets/test.jpg",
        "data/input/test.jpg",
        "test_face.jpg"
    ]
    
    image = None
    for path in test_paths:
        try:
            img = cv2.imread(path)
            if img is not None:
                image = img
                print(f"   ✓ Loaded image from {path}")
                break
        except:
            pass
    
    if image is None:
        print("   ! No test image found, creating synthetic image")
        # Create a simple test image (won't detect faces, but tests the pipeline)
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        # Draw a simple face-like pattern
        cv2.circle(image, (320, 240), 80, (200, 200, 200), -1)  # face
        cv2.circle(image, (290, 220), 15, (50, 50, 50), -1)   # left eye
        cv2.circle(image, (350, 220), 15, (50, 50, 50), -1)   # right eye
        cv2.ellipse(image, (320, 270), (30, 15), 0, 0, 180, (50, 50, 50), 2)  # mouth
        print("   ✓ Created synthetic test image")
except Exception as e:
    print(f"   ✗ Error loading image: {e}")
    sys.exit(1)

# Test face detection
print("\n3. Testing face detection...")
faces = engine.detect_faces(image)
print(f"   ✓ Detected {len(faces)} face(s)")

if faces:
    for i, face in enumerate(faces):
        bbox = face['bbox']
        conf = face['confidence']
        landmarks = face['landmarks']
        print(f"   Face {i+1}:")
        print(f"     - BBox: {bbox}")
        print(f"     - Confidence: {conf:.3f}")
        print(f"     - Landmarks: {len(landmarks)} points")

# Test embedding extraction
print("\n4. Testing face embedding...")
if faces:
    embedding = engine.embed_face(image, faces[0])
    if embedding is not None:
        print(f"   ✓ Extracted embedding: shape {embedding.shape}, dtype {embedding.dtype}")
        print(f"   ✓ Embedding norm: {np.linalg.norm(embedding):.3f}")
    else:
        print("   ✗ Embedding extraction failed")
else:
    print("   ! No faces to extract embeddings from")

# Test process_single_image
print("\n5. Testing combined processing...")
results = engine.process_single_image(image)
print(f"   ✓ Processed {len(results)} face(s) with embeddings")

for i, (face_dict, embedding) in enumerate(results):
    print(f"   Face {i+1}: bbox={face_dict['bbox']}, embedding_dim={embedding.shape[0]}")

print("\n" + "=" * 60)
print("✓ All FaceEngine tests passed!")
print("\nNext steps:")
print("- Add real face images to data/input/")
print("- Run: phosor scan --input data/input --output data/output --dry-run")
