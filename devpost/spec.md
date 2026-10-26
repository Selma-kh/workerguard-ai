---
doc: spec
status: approved
---

# Worker Safety AI — Technical Spec

## How This Works, In Plain Language
There are two programs, and both run on your laptop.

1. **The Python program (the "brain")** reads video from your laptop camera (or from a recorded clip) using OpenCV. On every frame, a YOLO model finds the people and the PPE (helmet, hi-vis vest), and a tracker gives each person an ID that stays the same from frame to frame. The program checks whether each person is inside the red zone and whether they are missing PPE. When a rule is broken, it saves an event (time, type, a snapshot image). It also draws the boxes, IDs and the red zone onto each frame.
2. **The Next.js dashboard (the "screen")** is the web page you look at. It shows the video the Python program sends, the three cards, the live alert list, the red banner, the Event Log and the CSV download. It also plays the siren sound and has the mute button.

The two programs talk like this: the video travels as a stream of images (MJPEG, an image the server keeps refreshing), and the numbers and alerts travel as a small piece of data (JSON) that the dashboard asks for twice a second.

Why this shape: the browser can't easily read a camera and run YOLO with tracking, but Python can. Next.js is only responsible for what you see. There is no database, no cloud and no login, so only the two programs are needed.

## The Core Journey Through the System
PRD ref: `prd.md > The Core Journey`.

1. You start both programs and open `http://localhost:3000`. The dashboard opens (no login) and asks for one click on **Start**, which also unlocks sound in the browser. → `prd.md > Screens and Layout`
2. You pick Live or Recorded with the switch. The dashboard tells the Python program which source to use. → `prd.md > Video source and switch`
3. Python reads a frame, runs detection and tracking, and draws boxes, IDs and the red zone. The dashboard shows the stream. → `prd.md > Detection`, `prd.md > Danger zone`
4. For each tracked person, Python checks: inside the zone? helmet? vest? If someone newly enters the zone or newly lacks PPE, it saves an event and a snapshot. → `prd.md > Counting rules (IDs, two people, re-entry)`
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
- **Detection:** an Ultralytics YOLO model (YOLO26, the newest in the docs, or YOLO11, the previous one) for people and tracking, plus PPE weights for helmet and vest. Her choice: accept the recommended approach, with the model version decided by which PPE weights actually work in testing.
- **Tracker:** the built-in BoT-SORT (default) or ByteTrack (faster, but may handle blocked views worse). Her request: use YOLO with a tracking model.
- **Storage:** none beyond local files. Events live in memory for the session; snapshots are image files in a local folder.
- **License:** the project is published under AGPL-3.0 (see Decisions and Open Issues).
- **Unverified, check early in the build:** current library versions; which PPE weights detect helmets and vests well on a laptop webcam and on the stock clip; the PPE models' dataset licenses (not stated on their pages); macOS camera permission for the terminal.

## Where It Runs and How Someone Tries It
- Everything runs locally on a Mac laptop. No deployment, no API keys and no cloud accounts are needed.
- Requirements: Python 3, Node.js, a laptop camera, and permission for the terminal app to use the camera.
- Start (two terminals):
  - Backend: from `backend/`, create a virtual environment, install `requirements.txt`, then run `uvicorn app.main:app --port 8000`.
  - Frontend: from `frontend/`, run `npm install` then `npm run dev`.
- Open `http://localhost:3000`, click Start, choose Live or Recorded.
- Demo recording: record the screen while a person walks in without a helmet or vest, then into the red zone, then open the Event Log and download the CSV.
- Submission needs a short demo video and a public GitHub repository. Deployment is optional and not planned. A README with these start steps goes in the repository.

## Look and Feel
PRD ref: `prd.md > Look and Feel`.
- Greys (steel, charcoal) as the base, deep blue as the accent for the top bar, sidebar and buttons, yellow/orange for missing-PPE alerts, red only for the danger zone, the banner and the siren state.
- A plain, clear sans-serif font. Professional, simple, factory-like, with no decorative styling.
- Layout follows her mock page [safe-watch-demo](https://safe-watch-demo.lovable.app/worker-safety-ai.html): status cards on top, video on the left, alert list on the right.
- Tailwind can honor all of this; the colors are set once as shared values so they stay consistent.

## Components

### Camera and Source Manager (backend)
Opens the laptop camera or the recorded clip, one at a time, and switches when asked. If it can't open the source, it reports "unavailable".
PRD ref: `prd.md > Video source and switch`, `prd.md > States and Boundaries` (camera or video fails).

### Detector and Tracker (backend)
Runs YOLO on each frame to find people, helmets and vests, and gives each person a persistent ID. Helmet and vest boxes are matched to the person whose box they sit inside.
PRD ref: `prd.md > Detection`.

### Zone and Rules Engine (backend)
Holds the fixed red zone rectangle (a setting in a config file). Marks a person as inside when their feet position (bottom-centre of their box) is inside the zone. Keeps each ID's state (inside/outside, helmet, vest) and creates an event only on a change: an ID entering the zone, or an ID newly missing the helmet or vest. A short grace period means a brief loss of detection doesn't create a new event. The rule is one event per person per missing item, which starts again only after they were seen wearing it.
PRD ref: `prd.md > Danger zone`, `prd.md > Counting rules (IDs, two people, re-entry)`.

### Frame Renderer and Video Stream (backend)
Draws boxes, IDs and the red zone on each frame and serves the result as an MJPEG stream.
PRD ref: `prd.md > Detection`, `prd.md > Danger zone`.

### Event Store and Snapshots (backend)
Keeps this session's events in memory and saves each snapshot (the frame with boxes, at the moment of the event) as an image file in a session folder. On start, the folder is emptied.
PRD ref: `prd.md > Event Log and CSV export`, `prd.md > States and Boundaries` (persistence).

### API (backend)
- `GET /video` — the MJPEG stream.
- `GET /api/state` — JSON with the counts (workers, violations, in danger zone), whether the zone is occupied, the source status, and the alert list.
- `POST /api/source` — body `{ "source": "live" | "recorded" }`.
- `GET /api/events` — the event table and the session summary.
- `GET /api/export.csv` — the CSV download.
- `GET /snapshots/{file}` — snapshot images.
PRD ref: `prd.md > Alerts and siren`, `prd.md > Event Log and CSV export`.

### App Shell (frontend)
Top bar with the project name and "System online" badge, and the collapsible sidebar with Dashboard and Event Log.
PRD ref: `prd.md > Screens and Layout`.

### Dashboard Page (frontend)
Three KPI cards, the video panel with the red banner over its top edge, the Live/Recorded switch, the mute button, the Start button, and the live alert list. Polls `/api/state` twice a second. Shows "Camera unavailable, check the connection" on a black panel when the source fails, and "No alerts, everything is fine" when the list is empty.
PRD ref: `prd.md > Video source and switch`, `prd.md > Alerts and siren`, `prd.md > States and Boundaries`.

### Siren Player (frontend)
Plays `siren.mp3` in a loop while the state says the zone is occupied and mute is off. Sound is allowed only after the Start click.
PRD ref: `prd.md > Alerts and siren`.

### Event Log Page (frontend)
Session summary (counts by type and a compliance figure), the table of time, type and snapshot thumbnail (click to enlarge), and the Download CSV button.
PRD ref: `prd.md > Event Log and CSV export`.

## Data Model
- **Event** (one per incident): `id`, `time`, `type` (`no_helmet`, `no_vest`, `zone_entry`), `person_id`, `snapshot_file`. Lives in memory in the backend for the session. Cleared on the next start.
- **Person state** (per tracked ID, in memory): `in_zone`, `has_helmet`, `has_vest`, `last_seen`. Lives only while the backend runs.
- **Session counters**: workers now, violations this session, in danger zone now. Computed from the above.
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
│   │   ├── detector.py      # YOLO + tracker, person/helmet/vest matching
│   │   ├── rules.py         # zone check, PPE check, event creation, grace period
│   │   ├── renderer.py      # draws boxes, IDs and the red zone, MJPEG output
│   │   ├── events.py        # in-memory events, snapshots, CSV, summary
│   │   └── config.py        # zone rectangle, thresholds, model paths
│   ├── models/              # PPE and YOLO weights (not committed if large or license-restricted)
│   ├── media/               # the recorded stock/self-filmed clip
│   ├── data/snapshots/      # generated snapshots (git-ignored)
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js pages
│   │   ├── layout.tsx       # app shell: top bar + collapsible sidebar
│   │   ├── page.tsx         # Dashboard
│   │   └── events/page.tsx  # Event Log
│   ├── components/          # KPI cards, video panel, alert list, banner, siren
│   ├── lib/api.ts           # calls to the backend
│   ├── public/siren.mp3     # royalty-free siren sound
│   └── package.json
├── devpost/                 # Devpost learning workspace
├── .gitignore
└── README.md                # how to start both programs
```

## External Services and Dependencies
No external services, accounts, API keys, hosting or cost.
- Libraries are installed locally: FastAPI, uvicorn, OpenCV, Ultralytics (see Stack for docs).
- **Model weights** (downloaded once): the YOLO base weights and a community PPE model. Examples found: [harsh-77/ppe-detection](https://huggingface.co/harsh-77/ppe-detection), [thalos-construction-ppe-v1](https://huggingface.co/thalostech2025/thalos-construction-ppe-v1). Check each license before publishing.
- **Media:** a freely licensed stock clip (for example from Pexels or Pixabay; not YouTube) or a clip she films, and a royalty-free siren sound. Keep the license information.

## Important Failure Modes
- **The PPE model misses helmets or vests, or flags them wrongly** → test early on the webcam and the clip; adjust the confidence threshold, try another weights file, or choose a clearer clip. Never fake the detection.
- **Camera can't open** (no permission, or in use) → the video panel is black and shows "Camera unavailable, check the connection"; the user can switch to Recorded.
- **Browser blocks the siren** → the Start button is the required first click. Until it is pressed the dashboard shows a prompt to start.
- **The backend isn't running or is slow** → the dashboard shows the same unavailable message and no invented numbers.
- **The laptop is slow** → use the smallest YOLO model, a lower video resolution, or process fewer frames per second.

## What Was Simplified and Why
- **Polling twice a second** instead of WebSockets — simpler to build and debug, and good enough for the demo. The fuller version would push events instantly.
- **Events in memory plus a snapshot folder** instead of a database — the log is session-only by decision, so nothing needs to survive a restart.
- **A fixed zone in a config file** instead of a draggable editor — decided in the PRD.
- **No login, accounts, cloud or multi-camera** — decided in the scope and PRD.
- **One source at a time** — decided in the PRD.
- **Siren played by the browser** — it keeps mute and sound in one place; a real site would use a physical siren.

## Decisions and Open Issues
**Decisions (her choices):**
- Next.js for the dashboard and Python with OpenCV for reading the camera.
- A YOLO model with a tracking model for IDs, and being told about newer models. YOLO26 and YOLO11 were presented; the version follows the PPE weights that work.
- Accepted the two-program local setup (Python backend and Next.js dashboard), with no cloud bucket. She answered "yes I follow you" to the recommendation; this is treated as agreement, and she can still change it.

- PPE alert rule (option A): one alert per person per missing item, again only after they were seen wearing it. Reason: it keeps the log honest and matches her "count on change" zone rule. Tradeoff: no record of how long someone stayed without PPE (a possible later feature). Siren stays for danger-zone entry only.
- License: publish the project under AGPL-3.0 (LICENSE file in the repo) because Ultralytics YOLO is AGPL-3.0 and the hackathon needs a public repo. The README notes that the PPE models' training datasets have unverified licenses. Tradeoff: a closed-source commercial version would need an Ultralytics Enterprise license or another detector. This is a reading of the license pages, not legal advice.

**Implementation details derived from these (not her choices):** FastAPI and uvicorn, Tailwind CSS, TypeScript, MJPEG streaming, polling twice a second, feet-position zone test, matching helmet and vest boxes to people, a grace period against lost detections, and one PPE event per person per missing item.

**Learner uncertainty:** how an agent and its tools work together. Clarified in the conversation: the model chooses a tool, the harness runs it and asks permission, and the result returns to the model. Check during the build: in `5-build`, point out one real tool call and one permission prompt and have her say what the harness did.

**Open issues:**
- Which PPE weights to use: decide in the first build step after a test on the webcam and the clip. Candidates (both AGPL-3.0, no published accuracy numbers): harsh-77/ppe-detection (Human, Helmet, No-Helmet, Vest; no "No-Vest" class, so a missing vest is inferred) and thalos-construction-ppe-v1 (hard hat, vest, gloves and their "no_" classes). Dataset licenses are unknown for both.
- Add a LICENSE file (AGPL-3.0) and the README license note before the repo goes public.
- From the PRD: the banner position (red bar over the top of the video) is the working choice. Snapshot files must stay out of the public repository.
- The DJI Osmo as a live camera is deferred.
