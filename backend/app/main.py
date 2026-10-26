"""The backend's web server: serves the video stream and the dashboard's data."""

import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from . import config
from .camera import pipeline

app = FastAPI(title="Worker Safety AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/state")
def state() -> dict:
    statuses = pipeline.statuses
    events = pipeline.events.all
    return {
        "status": pipeline.status,
        "workers": len(statuses),
        "in_zone": sum(1 for s in statuses if s.in_zone),
        "missing_helmet": sum(1 for s in statuses if not s.has_helmet),
        "missing_vest": sum(1 for s in statuses if not s.has_vest),
        "violations": len(events),
        "alerts": [e.to_dict() for e in reversed(events)][:50],  # newest first
    }


@app.post("/api/start")
def start() -> dict:
    pipeline.start()
    return {"status": pipeline.status}


@app.post("/api/stop")
def stop() -> dict:
    pipeline.stop()
    return {"status": pipeline.status}


def _mjpeg():
    """Yield the newest frame again and again as a multipart image stream."""
    last = None
    while True:
        jpeg = pipeline.latest_jpeg()
        if jpeg is not None and jpeg is not last:
            last = jpeg
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            )
        elif pipeline.status != "running":
            return  # source stopped or failed: end the stream
        else:
            time.sleep(0.02)


@app.get("/video")
def video() -> StreamingResponse:
    return StreamingResponse(
        _mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame"
    )
