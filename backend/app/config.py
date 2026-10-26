"""Settings for the backend. Everything tunable lives here."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detection model (people + tracking). Downloaded on first use.
PERSON_MODEL_PATH = BASE_DIR / "models" / "yolo26n.pt"
PERSON_CLASS_ID = 0  # "person" in the standard COCO classes
TRACKER = str(BASE_DIR / "app" / "tracker.yaml")  # ByteTrack with a longer memory
# Low on purpose: ByteTrack uses weak detections to keep an existing person's ID.
# New tracks still need a confident detection (see tracker.yaml).
CONFIDENCE = 0.1

# Laptop camera (0 = the default camera). For testing without a camera, set the
# environment variable WG_SOURCE to a video file path.
_env_source = os.environ.get("WG_SOURCE")
CAMERA_SOURCE: int | str = _env_source if _env_source else 0

# Video sent to the browser
STREAM_WIDTH = 960
JPEG_QUALITY = 80

# Browser addresses allowed to call the backend (the Next.js dashboard)
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
