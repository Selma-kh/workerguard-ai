"""Settings for the backend. Everything tunable lives here."""

import os
from pathlib import Path

import torch

BASE_DIR = Path(__file__).resolve().parent.parent

# Use the Mac's GPU when there is one, otherwise the CPU.
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# Person detection + tracking. Downloaded on first use.
PERSON_MODEL_PATH = BASE_DIR / "models" / "yolo26n.pt"
PERSON_CLASS_ID = 0  # "person" in the standard COCO classes
TRACKER = str(BASE_DIR / "app" / "tracker.yaml")  # ByteTrack with a longer memory
# Low on purpose: ByteTrack uses weak detections to keep an existing person's ID.
# New tracks still need a confident detection (see tracker.yaml).
CONFIDENCE = 0.1

# Helmet and hi-vis vest detection (community model harsh-77/ppe-detection).
PPE_MODEL_PATH = BASE_DIR / "models" / "ppe_harsh77.pt"
PPE_CONFIDENCE = 0.3
PPE_CLASS_NAMES = {"helmet": "helmet", "vest": "vest"}  # model class -> our item

# A helmet counts for a person if its centre is in the top part of their box;
# a vest if its centre is in the torso part. Fractions of the person's box height.
HELMET_ZONE = (-0.10, 0.35)
VEST_ZONE = (0.12, 0.80)

# PPE is judged over the last N frames, so one missed frame does not flicker the result.
PPE_HISTORY_FRAMES = 15
PPE_MIN_FRAMES_SEEN = 10  # a person must be seen this long before "missing" is declared
PPE_SEEN_FRACTION = 0.2  # item counts as worn if seen in at least this share of the frames

# Laptop camera (0 = the default camera). For testing without a camera, set the
# environment variable WG_SOURCE to a video file path.
_env_source = os.environ.get("WG_SOURCE")
CAMERA_SOURCE: int | str = _env_source if _env_source else 0

# Video sent to the browser
STREAM_WIDTH = 960
JPEG_QUALITY = 80

# Browser addresses allowed to call the backend (the Next.js dashboard)
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
