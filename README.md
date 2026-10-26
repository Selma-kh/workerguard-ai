# Worker Safety AI

A proof of concept for an HSE (health, safety and environment) manager. It watches one camera view, finds workers, flags a missing **helmet** or **hi-vis vest**, sounds a **siren** when someone enters a **danger zone**, and records every incident with a snapshot in an **Event Log** that can be exported as CSV.

It runs entirely on your laptop. No cloud, no accounts, no login.

> Built for the Devpost Learn "Build With AI: Basics" hackathon. This is a proof of concept, not a certified safety system. Do not rely on it to protect people.

## What it does

- Live laptop camera, or a recorded clip, one at a time (switch on the dashboard).
- Detects people and gives each one a stable ID ("Worker 3"). IDs are numbers, never names.
- Checks each person for a helmet and a vest. A missing item is flagged once per person, and again only after they were seen wearing it.
- One fixed red danger zone. A new violation is counted when someone **enters** it. Two people in the zone give two entries and one siren, which plays while anyone is inside (mute button on the dashboard).
- Dashboard: video with boxes and the red zone, a banner, three live counts (Workers, Violations, In danger zone) and the live alert list.
- Event Log: this session's incidents with time, type and snapshot, totals by type, and **Download CSV**. Each new session starts empty.
- Everything stays on your computer. Snapshots may show faces (face blur is not built yet).

## Requirements

- macOS or Linux, Python 3 (tested with 3.14), Node.js (tested with 24), a camera.
- On macOS, the app that launches the backend (Terminal, iTerm or VS Code) needs camera permission: System Settings, Privacy & Security, Camera.

## Setup (once)

```bash
# 1. Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python download_weights.py        # downloads the model weights into backend/models/

# 2. Frontend
cd ../frontend
npm install
```

## Run it

Use two terminals.

```bash
# Terminal 1: the Python backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --port 8000
```

The backend does not pick up code changes by itself. After editing anything in `backend/`, stop it (Ctrl+C) and start it again, or start it with `--reload` while developing.

```bash
# Terminal 2: the dashboard
cd frontend
npm run dev
```

Open <http://localhost:3000> and click **Start**. The first click also lets the browser play the siren.

### The Recorded source

Put any video (`.mp4`, `.mov`, `.webm`...) in `backend/media/`, then press **Recorded** on the dashboard. The first video in the folder is used and it loops. When a clip loops, the same workers keep their numbers, so a missing vest is not counted again, but a worker who walks into the danger zone on every pass is counted again. Use a freely licensed stock clip or one you film yourself, and keep its license information. Clips are git-ignored by default.

### Move the danger zone

Edit `DANGER_ZONE` in `backend/app/config.py` (left, top, right, bottom as fractions of the frame), then restart the backend.

## A one-minute demo

1. Click **Start** on Live. You appear boxed as "Worker 1".
2. Without a helmet or vest, you are flagged and a yellow/orange banner and alert appear.
3. Step into the red zone: the siren sounds, the banner turns red, and the cards update.
4. Step out: the siren stops. Press **Siren on** to mute it while the banner stays.
5. Open **Event Log**: each incident has a snapshot. Click **Download CSV**.

## How it works

```
Camera or clip -> OpenCV frame -> YOLO26 (people) + tracker (IDs) -> PPE model (helmet, vest)
              -> rules (zone entry, missing PPE) -> events + snapshots
FastAPI: /video (MJPEG stream)  /api/state  /api/events  /api/export.csv  /snapshots/*
Next.js dashboard: video, banner, cards, alerts, siren, Event Log
```

Files: `backend/app/` (`camera.py`, `detector.py`, `rules.py`, `renderer.py`, `events.py`, `config.py`, `main.py`) and `frontend/` (Next.js app and components). The plan lives in `devpost/` (scope, PRD, spec, checklist).

## Known limits

- Helmet and vest detection is best on clear, front-facing views. Bent-over or partly hidden workers are often missed, and a very dark or very distant person may be too.
- The tracker can still give a person a new ID if they are lost for a long time.
- No published accuracy numbers exist for the PPE model; test it on your own footage.
- One camera view at a time, one fixed zone, session-only log.

## License and credits

This project is released under the **GNU AGPL-3.0** (see `LICENSE`), because it uses Ultralytics YOLO, which is AGPL-3.0. A closed-source commercial product would need an Ultralytics Enterprise license or a different detector.

- [Ultralytics YOLO](https://docs.ultralytics.com/) (YOLO26 for people and tracking): AGPL-3.0.
- [harsh-77/ppe-detection](https://huggingface.co/harsh-77/ppe-detection) (helmet and vest model): listed as AGPL-3.0 and described by its author as for educational and research use. **Its training dataset and that dataset's license are not stated.**
- `frontend/public/siren.wav`: an original sound generated for this project.
- FastAPI, OpenCV, Next.js, React and Tailwind CSS under their own licenses.
