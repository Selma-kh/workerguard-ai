---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn at first (she confirmed slice 1 and tried it). After trying slice 1 she asked to build all remaining slices in one go and discuss afterwards, so slices 2-5 are built back to back, each still verified and committed, with her hands-on exploration at the end.

## Slices

- [x] **1. You can open the dashboard and see your laptop camera with people boxed and numbered**
  Becomes usable: Two programs running locally. Opening `http://localhost:3000` shows the app shell (top bar, sidebar with Dashboard and Event Log) and, after you click Start, the live laptop camera with a box and an ID such as "Worker 1" on each person, stable while they move.
  Why now: It proves the riskiest plumbing end to end first: Python version and library support, camera permission, YOLO with the tracker, and video reaching the browser. Everything else sits on this.
  PRD ref: `prd.md > The Core Journey` (steps 1-4), `prd.md > Screens and Layout`, `prd.md > Detection`
  Spec ref: `spec.md > Components` (Camera and Source Manager, Detector and Tracker, Frame Renderer and Video Stream, App Shell, Dashboard Page), `spec.md > File Structure`, `spec.md > Look and Feel`
  Build: Set up `backend/` (virtual environment, FastAPI, OpenCV, Ultralytics) and `frontend/` (Next.js with Tailwind); read the laptop camera, run YOLO person detection with the built-in tracker, draw boxes and IDs, serve `/video` as MJPEG; build the app shell and a Dashboard page with the Start button and the video panel in the agreed colors; add `.gitignore` entries for generated files.
  Verify (mechanical): Start both programs and confirm no errors; `curl` the `/video` endpoint and confirm it returns a multipart image stream; load `http://localhost:3000` and confirm the page renders; confirm detections with IDs appear in the backend output on a test image or camera frame.
  Learner check: Run the two start commands, open the page, click Start, and stand in front of the camera. You should see yourself boxed with an ID that stays the same as you move.
  Commit: `Add dashboard shell and live tracked camera view`

- [x] **2. The app tells apart a worker with a helmet and vest from one without**
  Becomes usable: Each tracked person shows whether they have a helmet and a hi-vis vest (yellow/orange marking when one is missing), using a PPE model chosen after testing.
  Why now: The PPE model is the biggest unknown (no published accuracy, unknown dataset licenses). Testing it now gives bad news early, while there is still time to switch models or footage.
  PRD ref: `prd.md > Detection`
  Spec ref: `spec.md > Components` (Detector and Tracker), `spec.md > Important Failure Modes`, `spec.md > Decisions and Open Issues` (PPE weights)
  Build: Download and compare the two candidate PPE weights on your webcam and a test image; pick one with you; add helmet and vest detection, match each helmet and vest to the person whose box contains it, and mark missing items on the video.
  Verify (mechanical): Run the detector on test images with and without a helmet and vest and confirm the per-person results; record which weights were chosen and their licenses in the spec.
  Learner check: Put on a helmet or a hi-vis item (or hold a picture of one) and take it off; the marking on your box should change.
  Commit: `Detect helmet and hi-vis vest per tracked person`

- [x] **3. A red danger zone, a siren, and live counts when someone steps into it**
  Becomes usable: A fixed red zone is drawn on the video. When a person steps in, the red banner appears over the video, the siren plays until the zone is empty (mute button works), and the cards Workers, Violations and In danger zone show real counts.
  Why now: This is the kernel from your scope: detection turning into action. It comes before the log and the polish so the idea is visible as early as possible.
  PRD ref: `prd.md > Danger zone`, `prd.md > Alerts and siren`, `prd.md > Counting rules (IDs, two people, re-entry)`, `prd.md > States and Boundaries` (empty)
  Spec ref: `spec.md > Components` (Zone and Rules Engine, API, Dashboard Page, Siren Player), `spec.md > Data Model`
  Build: Add the zone rectangle to `config.py` and draw it; add the zone check on the person's feet position with per-ID in/out state and the grace period; add `/api/state` and poll it twice a second; add the three cards, the banner, the "No alerts, everything is fine" state, the royalty-free siren sound with the Start click and the mute button.
  Verify (mechanical): Feed a recorded test clip with a person crossing the zone and confirm the state flips to occupied and back; confirm two people inside produce a count of 2 and one siren state; confirm a brief detection gap does not add a violation; confirm `/api/state` values.
  Learner check: Click Start, walk into the red zone: you should hear the siren and see the banner and the card change; step out and it should stop; press mute and the sound should stop while the banner stays.
  Commit: `Add danger zone, banner, siren and live counts`

- [x] **4. Every incident is recorded with a snapshot, in an Event Log you can export**
  Becomes usable: Each missing-PPE alert (one per person per missing item) and each zone entry appears in the live alert list and in the Event Log page with a time, type and snapshot thumbnail; the session summary shows totals by type and a compliance figure; Download CSV works.
  Why now: It completes the kernel (the incident is recorded, not just heard) and builds on the rules from slice 3.
  PRD ref: `prd.md > Alerts and siren`, `prd.md > Counting rules (IDs, two people, re-entry)`, `prd.md > Event Log and CSV export`, `prd.md > States and Boundaries` (persistence)
  Spec ref: `spec.md > Components` (Event Store and Snapshots, API, Event Log Page), `spec.md > Data Model`
  Build: Create events on zone entry and on new missing PPE per rule A, save snapshots to `backend/data/snapshots/` (emptied on start), serve `/api/events`, `/api/export.csv` and the snapshots, fill the live alert list, and build the Event Log page with summary, table, thumbnail enlarge and Download CSV.
  Verify (mechanical): Trigger one zone entry and one missing helmet from a test clip and confirm two rows with snapshot files; confirm a person staying in the zone for a minute gives one row; confirm the summary equals the row counts; download the CSV and confirm the rows match.
  Learner check: Walk in without a helmet, then into the zone; open the Event Log and confirm two rows with photos; download the CSV and open it in a spreadsheet; restart and confirm the log starts empty.
  Commit: `Record incidents with snapshots, summary and CSV export`

- [x] **5. Switch to a recorded clip, handle a failed camera, and make it ready to share**
  Becomes usable: The Live/Recorded switch works with a freely licensed or self-filmed clip; a failed source shows the black panel with "Camera unavailable, check the connection"; the README, LICENSE (AGPL-3.0) and git ignores are ready for the public repository.
  Why now: The switch is your demo backup, and the failure state and repository hygiene are the last pieces before final review.
  PRD ref: `prd.md > Video source and switch`, `prd.md > States and Boundaries` (camera or video fails), `prd.md > Look and Feel`
  Spec ref: `spec.md > Components` (Camera and Source Manager, Dashboard Page), `spec.md > Where It Runs and How Someone Tries It`, `spec.md > Important Failure Modes`, `spec.md > Decisions and Open Issues` (license)
  Build: Add `POST /api/source` and the switch; add the chosen clip to `backend/media/` with its license noted; show the camera-unavailable state; add the README with the two start commands and what to show in the demo, the AGPL-3.0 LICENSE, the dataset-license note, and git ignores for snapshots, weights and environments.
  Verify (mechanical): Switch between sources with `curl` and in the page and confirm the video changes and counts keep going; unplug or block the camera and confirm the failure message; follow the README from a clean checkout and confirm both programs start; confirm `git status` shows no snapshots, weights or secrets staged.
  Learner check: Press Recorded, then Live; block the camera permission and confirm the message; read the README and say whether you could start it from scratch.
  Commit: `Add source switch, camera failure state, README and license`

## Hands-on Checkpoints

- [ ] Early usable behavior explored — after slice 3 (the siren and zone kernel), because feedback there can still change the log and polish
- [ ] Final kick-the-tires exploration and feedback completed

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: not started
Route and stops: not started
Edit outcome: not started
Reflection: not started
Activity mode: not started

## Revisions

- Tracker memory and confidence changed (ByteTrack track_buffer 30 to 90, detection confidence 0.4 to 0.1, custom `backend/app/tracker.yaml`) — when she tried slice 1 live, IDs climbed to "Worker 66" after she moved. Simulated detection gaps gave 12 IDs for 4 people with the original settings and 4 with the new ones.
- PPE weights chosen: harsh-77/ppe-detection — both candidates read helmets and vests well on real worker photos, but harsh-77 ran at about 11 ms/frame on the Mac GPU (33 ms on CPU) against 57 ms (258 ms) for the thalos model, and is 5 MB against 88 MB. Tradeoff: no gloves class. Both files were scanned with picklescan (no dangerous code) before being loaded. Limitation found: bent-over or partly hidden workers are often missed, so demo footage should show workers clearly from the front.
- Worker numbers reached 17-28 for one person when she tried it live (close-up face view, the box size jumps, and the chair in the zone may have been read as a person for a moment). A simulation with size jumps gave 4 tracker IDs for 1 person. Fix in `rules.py`: a person only counts after 5 frames, a newly confirmed person near someone lost less than 2 s ago takes over that person's number and history, and the numbers shown are our own, starting at 1 each session. Tracker `match_thresh` also raised from 0.8 to 0.95. On the same simulation only "Worker 1" is shown. Known tradeoff: two different people who swap places within 2 seconds could be merged.
- A second live test still showed 5 workers for one person (numbers 1 to 5 alternating, one huge close-up box). Added duplicate-box suppression (a box mostly inside another person's box is the same person), a longer takeover window (4 s, 2 box sizes), and an optional `WG_DEBUG=1` log of raw tracker numbers. Simulated duplicate-box, tracker-ID-swap and two-people cases all give the right number of workers. Not yet confirmed on her live camera.
- A flickering false vest detection reset the missing-PPE rule and created duplicate incidents; after an incident the item must now be seen worn for about 3 seconds in a row before the rule re-arms, and leaving the zone must be confirmed for 12 frames instead of 6.
- No stock clip is shipped with the project. Candidate Wikimedia Commons videos were far too large (100 MB to 1.2 GB) and not clear shots of workers, so the Recorded source plays the first video in `backend/media/` (git-ignored) and the dashboard says "No recorded clip found" if the folder is empty. She adds a freely licensed stock clip or films one herself, as her PRD allows.
- A looping clip used to restart the tracker and give the same people new worker numbers (her screenshot: Workers 3 and 4 after the restart, Violations 4 for 2 people). The loop now keeps numbers and history (`RulesEngine.tracker_reset`). Over three loops of the first demo clip: worker numbers 1 and 2 only (before: 1 to 6); the missing vest is counted once, and the zone entry once per pass (a real re-entry).
- The KPI cards go under the video (she asked for this; the PRD sketch had them above), and the dashboard gets a darker factory/control-room style (hazard stripes, camera-frame corners, LED status lights). The PRD is updated to match.
