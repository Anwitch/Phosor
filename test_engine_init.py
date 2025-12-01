"""Quick test script to verify FaceEngine initialization."""

import sys
sys.path.insert(0, 'src')

from core.face_engine import FaceEngine

print("Creating FaceEngine instance...")
print("This will download models on first run (~50MB)")
print("-" * 60)

try:
    engine = FaceEngine()
    print("✓ FaceEngine initialized successfully!")
    print(f"✓ Detector: {type(engine.detector).__name__}")
    print(f"✓ Recognizer: {type(engine.recognizer).__name__}")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

print("-" * 60)
print("Models are cached in: ~/.uniface/models/")
print("FaceEngine is ready to use!")
