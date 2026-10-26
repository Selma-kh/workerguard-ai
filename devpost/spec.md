---
doc: spec
status: approved
---

# Worker Safety AI — Technical Spec

## How This Works, In Plain Language
There are two programs, and both run on your laptop.

1. **The Python program (the "brain")** reads video from your laptop camera (or from a recorded clip) using OpenCV. On every frame, one YOLO model (YOLO26) finds the people and a tracker gives each one an ID, while a second model trained for protective equipment finds helmets and hi-vis vests. The rules then give each confirmed person a worker number (Worker 1, Worker 2...) that stays the same even if the tracker changes its own ID. The program checks whether each person is inside the red zone and whether they are missing PPE. When a rule is broken, it saves an event (time, type, a snapshot image). It also draws the boxes, IDs and the red zone onto each frame.
2. **The Next.js dashboard (the "screen")** is the web page you look at. It shows the video the Python program sends, the three cards, the live alert list, the red banner, the Event Log and the CSV download. It also plays the siren sound and has the mute button.

The two programs talk like this: the video travels as a stream of images (MJPEG, an image the server keeps refreshing), and the numbers and alerts travel as a small piece of data (JSON) that the dashboard asks for twice a second.

Why this shape: the browser can't easily read a camera and run YOLO with tracking, but Python can. Next.js is only responsible for what you see. There is no database, no cloud and no login, so only the two programs are needed.

## The Core Journey Through the System
PRD ref: `prd.md > The Core Journey`.

1. You start both programs and open `http://localhost:3000`. The dashboard opens (no login) and asks for one click on **Start**, which also unlocks sound in the browser. → `prd.md > Screens and Layout`
2. You pick Live or Recorded with the switch. The dashboard tells the Python program which source to use. → `prd.md > Video source and switch`
3. Python reads a frame, runs detection and tracking, and draws boxes, IDs and the red zone. The dashboard shows the stream. → `prd.md > Detection`, `prd.md > Danger zone`
4. For each confirmed person, Python checks: inside the zone? helmet? vest? If someone newly enters the zone or newly lacks PPE, it saves an event and a snapshot. → `prd.md > Counting rules (IDs, two people, re-entry)`
5. The dashboard asks Python for the current state twice a second. It updates the cards and the alert list, shows the red banner, and plays the siren while someone is in the zone (unless muted). → `prd.md > Alerts and siren`
6. You open the Event Log: the table, the session summary, and Download CSV. → `prd.md > Event Log and CSV export`
7. You close the programs. On the next start, everything begins empty. → `prd.md > States and Boundaries`

```
 Camera / clip ──► OpenCV frame ──► YOLO (person + PPE) ──► Tracker (IDs)
                                                              │
                      zone check + PPE check ◄────────────────┘
                              │
              new violation? ─┴─► save event + snapshot (memory + local folder)
                              │
   FastAPI:  /video (stream)  /api/state (poll)  /api/export.csv  /snapshots/*
                              │
                       Next.js dashboard
```

## Stack
- **Backend:** Python 3, FastAPI (web server), uvicorn (runs it), OpenCV (camera and drawing), Ultralytics (YOLO and the built-in tracker). Docs: [FastAPI](https://fastapi.tiangolo.com/), [OpenCV](https://docs.opencv.org/), [Ultralytics models](https://docs.ultralytics.com/models/), [Ultralytics track mode](https://docs.ultralytics.com/modes/track/).
- **Frontend:** Next.js (React) with Tailwind CSS for styling. Docs: [Next.js](https://nextjs.org/docs). Next.js was her choice; Tailwind and TypeScript are implementation details derived from it.
- **Detection:** YOLO26n (`yolo26n.pt`, Ultralytics) for people, and the community model harsh-77/ppe-detection (`ppe_harsh77.pt`, YOLO11-based, classes helmet, human, no-helmet, vest; only helmet and vest are used) for PPE. Both candidate PPE models were tested on real worker photos; harsh-77 was chosen because it ran about 5 times faster (11 ms against 57 ms per frame on the Mac GPU, 33 ms against 258 ms on CPU) and is 5 MB. It was scanned with picklescan before loading. Runs on the Mac GPU (MPS) when available, otherwise the CPU.
- **Tracker:** ByteTrack, built into Ultralytics, with a custom `backend/app/tracker.yaml` (longer memory: `track_buffer` 90, `match_thresh` 0.95) and a low detection confidence (0.1) so weak detections can keep an existing ID. Her request: use YOLO with a tracking model.
- **Storage:** none beyond local files. Events live in memory for the session; snapshots are image files in a local folder.
- **License:** the project is published under AGPL-3.0 (see Decisions and Open Issues).
- **Versions used in the build:** Python 3.14, Ultralytics 8.4.x, FastAPI 0.162, OpenCV 5, PyTorch 2.14, Next.js 16, Node 24.
- **Still unverified:** the PPE model's training dataset and its license (not stated on its page); accuracy on her own live camera (tested on stock photos and videos, not on her camera).

## Where It Runs and How Someone Tries It
- Everything runs locally on a Mac laptop. No deployment, no API keys and no cloud accounts are needed.
- Requirements: Python 3, Node.js, a laptop camera, and permission for the terminal app to use the camera.
- Start (two terminals):
  - Backend: from `backend/`, create a virtual environment, install `requirements.txt`, run `python download_weights.py` once, then `uvicorn app.main:app --port 8000`. The backend does not reload by itself: restart it after code changes (or use `--reload`).
  - Frontend: from `frontend/`, run `npm install` then `npm run dev`.
- Open `http://localhost:3000`, click Start, choose Live or Recorded. Recorded plays the first video in `backend/media/` (git-ignored; add a stock or self-filmed clip).
- Demo recording: record the screen while a person walks in without a helmet or vest, then into the red zone, then open the Event Log and download the CSV.
- Submission needs a short demo video and a public GitHub repository. Deployment is optional and not planned. A README with these start steps goes in the repository.

## Look and Feel
PRD ref: `prd.md > Look and Feel`.
- An industrial control-room style (she found the first light, plain version too simple): dark charcoal base, steel panels, a deep blue sidebar, yellow/black hazard stripes under the top bar, camera-frame corner marks with "CAM-01 · ZONE A" and a clock over the video, an LED-style status light, and monospace numbers on the cards.
- Yellow/orange marks missing PPE; red is only for the danger zone, the red banner and the siren state.
- Layout: video on the left with the source switch and the three KPI cards **under** it (her request), the live alert list on the right. Reference: her mock page [safe-watch-demo](https://safe-watch-demo.lovable.app/worker-safety-ai.html).
- Tailwind CSS with the colors defined once in `frontend/app/globals.css`.

## Components

### Camera and Source Manager (backend)
Opens the laptop camera or the first clip in `backend/media/`, one at a time, and switches when asked (switching keeps the session's log). A recorded clip plays at its own speed and loops; at each loop the same people keep their worker numbers. If a source can't be opened, it reports "unavailable". Start begins a new session (empty log, numbers from 1).
PRD ref: `prd.md > Video source and switch`, `prd.md > States and Boundaries` (camera or video fails).

### Detector and Tracker (backend)
Runs the person model with ByteTrack on each frame (tracker IDs) and the PPE model on the same frame (helmet and vest boxes). Optional `WG_DEBUG=1` writes the raw tracker numbers to `backend/data/debug.log`.
PRD ref: `prd.md > Detection`.

### Zone and Rules Engine (backend)
Holds the fixed red zone rectangle (`DANGER_ZONE` in `config.py`, fractions of the frame, reaching the edges). Turns tracker IDs into stable worker numbers: a person only counts after 5 frames (ignores ghost detections), a box mostly inside another is the same person detected twice and is dropped, and a newly confirmed person near someone lost less than 4 seconds ago takes over that worker's number and history. A helmet or vest belongs to a person if its centre is in the head or torso band of their box, judged over the last 15 frames. A person is inside the zone when their feet position (bottom-centre of the box) is inside it, confirmed for 3 frames to enter and 12 to leave. Events are created only on a change: a worker entering the zone, or a worker newly missing a helmet or vest. A missing-PPE incident can only repeat after the worker was seen wearing the item for about 3 seconds in a row.
PRD ref: `prd.md > Danger zone`, `prd.md > Counting rules (IDs, two people, re-entry)`.

### Frame Renderer and Video Stream (backend)
Draws boxes, IDs and the red zone on each frame and serves the result as an MJPEG stream.
PRD ref: `prd.md > Detection`, `prd.md > Danger zone`.

### Event Store and Snapshots (backend)
Keeps this session's events in memory and saves each snapshot (the frame with boxes, at the moment of the event) as an image file in a session folder. On start, the folder is emptied.
PRD ref: `prd.md > Event Log and CSV export`, `prd.md > States and Boundaries` (persistence).

### API (backend)
- `GET /video` — the MJPEG stream.
- `GET /api/state` — JSON with the source and status, the counts (workers, in_zone, missing_helmet, missing_vest, workers_with_violation, violations = incidents) and the alert list (newest first).
- `POST /api/start`, `POST /api/stop` — start a new session / stop it.
- `POST /api/source` — body `{ "source": "live" | "recorded" }`.
- `GET /api/events` — the event table and the session summary.
- `GET /api/export.csv` — the CSV download.
- `GET /snapshots/{file}` — snapshot images.
PRD ref: `prd.md > Alerts and siren`, `prd.md > Event Log and CSV export`.

### App Shell (frontend)
Top bar with the project name and "System online" badge, and the collapsible sidebar with Dashboard and Event Log.
PRD ref: `prd.md > Screens and Layout`.

### Dashboard Page (frontend)
The video panel with the red or orange banner over its top edge and a camera-frame look, the Live/Recorded switch, the three KPI cards under the video (Workers, Violations = workers with at least one incident, In danger zone), the mute button, the Start/Stop button, and the live alert list. Polls `/api/state` twice a second. Shows "Camera unavailable, check the connection" on a black panel when the source fails, and "No alerts, everything is fine" when the list is empty.
PRD ref: `prd.md > Video source and switch`, `prd.md > Alerts and siren`, `prd.md > States and Boundaries`.

### Siren Player (frontend)
Plays `siren.wav` (an original sound generated for the project) in a loop while the state says the zone is occupied and mute is off. Sound is allowed only after the Start click.
PRD ref: `prd.md > Alerts and siren`.

### Event Log Page (frontend)
Session summary (incidents, counts by type, and the share of workers with no violation), the table of time, type and snapshot thumbnail (click to enlarge), and the Download CSV button.
PRD ref: `prd.md > Event Log and CSV export`.

## Data Model
- **Event** (one per incident): `id`, `time`, `type` (`no_helmet`, `no_vest`, `zone_entry`), `person_id`, `snapshot_file`. Lives in memory in the backend for the session. Cleared on the next start.
- **Person state** (per worker number, in memory): helmet and vest history, `in_zone`, whether each missing-PPE incident is active, `last_seen`, last box. Lives only while the backend runs.
- **Session counters**: workers now, workers with at least one incident, incidents this session, in danger zone now. Computed from the above.
- **Snapshots**: image files in `backend/data/snapshots/` (emptied on start, ignored by git).
- **CSV**: generated on download from the events, with columns time, type, person ID, snapshot file name.
- **Dashboard state**: nothing is stored in the browser. Closing the tab and reopening it shows the backend's current session.

## File Structure
```
workerguard-ai/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app and API routes
│   │   ├── camera.py        # live camera / recorded clip, source switching
│   │   ├── detector.py      # YOLO26 + ByteTrack (people) and the PPE model (helmet, vest)
│   │   ├── tracker.yaml     # ByteTrack settings (longer memory)
│   │   ├── rules.py         # worker numbers, zone check, PPE check, incident creation
│   │   ├── renderer.py      # draws boxes, IDs and the red zone, MJPEG output
│   │   ├── events.py        # in-memory events, snapshots, CSV, summary
│   │   └── config.py        # zone rectangle, thresholds, model paths
│   ├── download_weights.py  # downloads the model weights into models/
│   ├── models/              # YOLO26n and PPE weights (git-ignored)
│   ├── media/               # the recorded clip (git-ignored)
│   ├── data/snapshots/      # generated snapshots (git-ignored)
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js pages
│   │   ├── layout.tsx       # app shell: top bar + collapsible sidebar
│   │   ├── page.tsx         # Dashboard
│   │   └── events/page.tsx  # Event Log
│   ├── components/          # AppShell, BackendProvider, VideoPanel (with banner), KpiCards, AlertList
│   ├── lib/useSiren.ts      # plays the siren while the zone is occupied
│   ├── lib/api.ts           # calls to the backend
│   ├── public/siren.wav     # original siren sound generated for the project
│   └── package.json
├── devpost/                 # Devpost learning workspace
├── .gitignore
├── LICENSE                  # AGPL-3.0
└── README.md                # how to set up and start both programs
```

## External Services and Dependencies
No external services, accounts, API keys, hosting or cost.
- Libraries are installed locally: FastAPI, uvicorn, OpenCV, Ultralytics (see Stack for docs).
- **Model weights** (downloaded once with `download_weights.py`): `yolo26n.pt` from Ultralytics and the PPE model [harsh-77/ppe-detection](https://huggingface.co/harsh-77/ppe-detection) (AGPL-3.0 on its page; for educational and research use; dataset not stated). The other candidate, [thalos-construction-ppe-v1](https://huggingface.co/thalostech2025/thalos-construction-ppe-v1), was tested and not used.
- **Media:** a freely licensed stock clip or a clip she films, kept in `backend/media/` and not committed. The test clips came from Pexels (free to use; check each clip's license page). The siren sound is original.

## Important Failure Modes
- **The PPE model misses helmets or vests, or flags them wrongly** → test early on the webcam and the clip; adjust the confidence threshold, try another weights file, or choose a clearer clip. Never fake the detection.
- **Camera can't open** (no permission, or in use) → the video panel is black and shows "Camera unavailable, check the connection"; the user can switch to Recorded.
- **Browser blocks the siren** → the Start button is the required first click. Until it is pressed the dashboard shows a prompt to start.
- **The backend isn't running or is slow** → the dashboard shows the same unavailable message and no invented numbers.
- **A person gets several worker numbers** (close-up face views make the box change size, or the model draws two boxes) → the confirmation, duplicate-box and number-takeover rules in the Zone and Rules Engine, plus optional `WG_DEBUG=1` to inspect raw tracker numbers. Not fully eliminated: two different people swapping places within a few seconds could be merged.
- **The laptop is slow** → use the smallest YOLO model, a lower video resolution, or process fewer frames per second.

## What Was Simplified and Why
- **Polling twice a second** instead of WebSockets — simpler to build and debug, and good enough for the demo. The fuller version would push events instantly.
- **Events in memory plus a snapshot folder** instead of a database — the log is session-only by decision, so nothing needs to survive a restart.
- **A fixed zone in a config file** instead of a draggable editor — decided in the PRD.
- **No login, accounts, cloud or multi-camera** — decided in the scope and PRD.
- **One source at a time** — decided in the PRD.
- **No stock clip shipped** — the Recorded source plays any clip placed in `backend/media/`; it keeps the repository small and avoids committing videos of real people.
- **Siren played by the browser** — it keeps mute and sound in one place; a real site would use a physical siren.

## Decisions and Open Issues
**Decisions (her choices):**
- Next.js for the dashboard and Python with OpenCV for reading the camera.
- A YOLO model with a tracking model for IDs, and being told about newer models. YOLO26 was used for people; the PPE model is harsh-77 (YOLO11-based), chosen after a test.
- The Violations card counts workers with at least one incident, while the Event Log counts every incident ("Incidents").
- The Event Log and counts are session-only: each Start begins empty.
- Accepted the two-program local setup (Python backend and Next.js dashboard), with no cloud bucket. She answered "yes I follow you" to the recommendation; this is treated as agreement, and she can still change it.

- PPE alert rule (option A): one alert per person per missing item, again only after they were seen wearing it. Reason: it keeps the log honest and matches her "count on change" zone rule. Tradeoff: no record of how long someone stayed without PPE (a possible later feature). Siren stays for danger-zone entry only.
- License: publish the project under AGPL-3.0 (LICENSE file in the repo) because Ultralytics YOLO is AGPL-3.0 and the hackathon needs a public repo. The README notes that the PPE models' training datasets have unverified licenses. Tradeoff: a closed-source commercial version would need an Ultralytics Enterprise license or another detector. This is a reading of the license pages, not legal advice.

**Implementation details derived from these (not her choices):** FastAPI and uvicorn, Tailwind CSS, TypeScript, MJPEG streaming, polling twice a second, feet-position zone test, matching helmet and vest boxes to people, confirmation, duplicate-box and number-takeover rules, hysteresis on entering and leaving the zone, a 3-second re-arm for missing-PPE incidents, and the control-room styling.

**Learner uncertainty:** how an agent and its tools work together. Clarified in the conversation: the model chooses a tool, the harness runs it and asks permission, and the result returns to the model. Check during the build: in `5-build`, point out one real tool call and one permission prompt and have her say what the harness did.

**Resolved during the build:** PPE weights chosen (harsh-77); LICENSE (AGPL-3.0) and README license note added; the banner is a red or orange bar over the top of the video.

**Open issues:**
- Accuracy of helmet and vest detection on her own live camera and footage: tested on stock photos and videos only. Works best on clear, front or back views; bent-over, half-hidden or dark-helmet-from-behind cases are missed.
- The PPE model's training dataset and its license are unknown.
- Snapshot files and recorded clips must stay out of the public repository (they are git-ignored).
- Resolved: missing-PPE alerts stay in the live list, the banner and the Event Log (option A); she confirmed keeping them all.
- The DJI Osmo as a live camera is deferred.
