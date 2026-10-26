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
# After a missing-PPE incident, the item must be seen worn for this many frames in a row
# before the same person can trigger a new incident for it (about 3 seconds).
PPE_REARM_FRAMES = 60

# The danger zone: a fixed rectangle, as fractions of the frame (left, top, right, bottom).
# Change these numbers to move the red zone.
DANGER_ZONE = (0.55, 0.40, 1.0, 1.0)  # reaches the frame edges so nobody "slips" under it
# A person must be seen inside/outside for this many frames before it counts, so someone
# standing on the edge does not create a stream of enter/leave events.
ZONE_ENTER_FRAMES = 3
ZONE_EXIT_FRAMES = 12
# A person only counts after being tracked for this many frames (ignores ghost detections).
CONFIRM_FRAMES = 5
# A newly confirmed person who appears near someone lost less than this long ago (and within
# ADOPT_DISTANCE box sizes of where they were) is treated as the same person.
ADOPT_SECONDS = 4.0
ADOPT_DISTANCE = 2.0
# Two boxes where the smaller is this much inside the other are the same person.
DUPLICATE_OVERLAP = 0.7
# People not seen for this long are forgotten (a later return counts as new).
FORGET_AFTER_SECONDS = 8

# Laptop camera (0 = the default camera). For testing without a camera, set the
# environment variable WG_SOURCE to a video file path.
_env_source = os.environ.get("WG_SOURCE")
CAMERA_SOURCE: int | str = _env_source if _env_source else 0

# The "Recorded" source plays the first video found in this folder (stock or self-filmed).
MEDIA_DIR = BASE_DIR / "media"
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi"}


def find_clip() -> Path | None:
    if not MEDIA_DIR.exists():
        return None
    clips = sorted(p for p in MEDIA_DIR.iterdir() if p.suffix.lower() in VIDEO_EXTENSIONS)
    return clips[0] if clips else None


# Where snapshots of incidents are saved (emptied at the start of every session).
SNAPSHOT_DIR = BASE_DIR / "data" / "snapshots"

# Set WG_DEBUG=1 to write the tracker's raw numbers (IDs, boxes, confidence; no images)
# to backend/data/debug.log, to investigate tracking problems.
DEBUG_LOG = BASE_DIR / "data" / "debug.log" if os.environ.get("WG_DEBUG") else None

# Video sent to the browser
STREAM_WIDTH = 960
JPEG_QUALITY = 80

# Browser addresses allowed to call the backend (the Next.js dashboard)
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
