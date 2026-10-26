"""The backend's web server: serves the video stream and the dashboard's data."""

import time
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
        "source": pipeline.source,
        "clip_available": config.find_clip() is not None,
        "workers": len(statuses),
        "in_zone": sum(1 for s in statuses if s.in_zone),
        "missing_helmet": sum(1 for s in statuses if not s.has_helmet),
        "missing_vest": sum(1 for s in statuses if not s.has_vest),
        "violations": len(events),  # incidents this session
        "workers_with_violation": pipeline.events.workers_with_violation(),
        "alerts": [e.to_dict() for e in reversed(events)][:50],  # newest first
    }


@app.get("/api/events")
def events() -> dict:
    return {
        "summary": pipeline.events.summary(),
        "events": [e.to_dict() for e in reversed(pipeline.events.all)],  # newest first
    }


@app.get("/api/export.csv")
def export_csv() -> Response:
    return Response(
        pipeline.events.to_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="incident-log.csv"'},
    )


@app.post("/api/start")
def start() -> dict:
    pipeline.start()
    return {"status": pipeline.status}


class SourceChoice(BaseModel):
    source: Literal["live", "recorded"]


@app.post("/api/source")
def set_source(choice: SourceChoice) -> dict:
    pipeline.set_source(choice.source)
    return {"status": pipeline.status, "source": pipeline.source}


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


# Snapshot images of incidents, shown in the Event Log.
config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/snapshots", StaticFiles(directory=str(config.SNAPSHOT_DIR)), name="snapshots")
