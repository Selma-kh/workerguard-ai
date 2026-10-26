---
doc: prd
status: approved
---

# Worker Safety AI — Product Requirements

A safety dashboard for an HSE manager that watches one camera view, detects workers, flags missing helmet or vest and danger-zone entry, sounds a siren, and records every incident. "Worker Safety AI" is the working title; Third Eye, Worker Safe and Safe AI are candidates (pick before shipping).
Source: `scope.md > The Unique Kernel`, `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`, `scope.md > The POC Boundary`.

## The Core Journey
1. The manager opens the app and lands directly on the **Dashboard** (there is no login).
2. They see the top bar, a sidebar with **Dashboard** and **Event Log**, three KPI cards, the video area, the source switch, and the live alert list.
3. They choose the video source with the switch: **Live** (the laptop webcam) or **Recorded** (a freely licensed stock clip, not YouTube, or a clip they filmed).
4. The video plays with a box around each detected person, a short ID (for example "Worker 1"), and a fixed red danger zone drawn over the floor.
5. When a worker is missing a helmet or a hi-vis vest, or enters the danger zone, the alert happens: a red (zone) or orange (missing PPE) banner appears over the video, the alert is added to the live list, and the KPI cards update. The siren sounds for danger-zone entry only.
6. When the situation is resolved (the worker puts the PPE on, or leaves the zone), the siren stops and the banner disappears.
7. The manager opens the **Event Log** to see every incident with a snapshot, a summary of totals by type, and can download the log as a CSV.
8. Success: in a one-minute demo, a worker is detected, triggers an alert, the siren sounds, and the incident appears in the log.

## Screens and Layout
Two screens, reached from a collapsible sidebar. No login page, no profile menu, no configuration page.

**Top bar (on every screen):** the project name on the left and a status badge on the right ("System online" while a source is running).

**Sidebar:** two items, Dashboard and Event Log. It can be collapsed and expanded with a button.

**Dashboard**
- Three KPI cards **under the video** (she asked for them there): **Workers** (people detected right now), **Violations** (how many different workers have at least one incident this session; the Event Log counts every incident), **In danger zone** (people inside the red zone right now). The numbers are real counts from the video, never estimates.
- Left: the **video panel** with boxes, IDs, and the red danger zone. The red alert banner sits across the top of this panel. Under it, the **source switch**: Live or Recorded.
- Right: the **live alert list**.
- The **mute button** for the siren is on the dashboard.

**Event Log**
- Summary at the top covering the current session: total violations split by type (missing helmet, missing vest, entered danger zone), plus a compliance figure.
- Below it, a table with one row per incident: time, type, and a snapshot image.
- A **Download CSV** button.

## Look and Feel
- Professional and recalling factories, industry and accidents; she found the first light, plain version too simple, so the style is an industrial control room: dark charcoal base, steel panels, monospace numbers, yellow/black hazard-stripe accents, camera-frame corner marks with a "CAM-01" label and timestamp over the video, and LED-style status lights.
- Base: steel and charcoal greys.
- Accent: deep blue (from her "Blue Edition" sales deck) for headings, sidebar and buttons.
- Yellow/orange is an accent used for missing-PPE alerts. Red is reserved for danger-zone entry, the banner and the siren state.
- A plain, clear sans-serif font; nothing decorative.
- Reference layout: her mock page https://safe-watch-demo.lovable.app/worker-safety-ai.html (status cards, camera panel, alert list).
- No warning or green zones are drawn; only the red danger zone.

## Features and Behavior

### Video source and switch
One camera view is shown at a time. The switch chooses its source: Live or Recorded. Recorded plays the first video found in `backend/media/` (a freely licensed stock clip, not YouTube, or a clip the learner films) and loops it; the same workers keep their numbers when it restarts.
- As a safety manager, I want to choose between a live camera and a recorded clip so that I can demo reliably.
  - [ ] Pressing Live shows the laptop webcam feed; pressing Recorded plays the clip.
  - [ ] Only one source is shown and analysed at a time.
  - [ ] Switching sources does not reset the log or the Violations total.

### Detection
Detects people and two PPE items: a helmet and a hi-vis vest. Each person gets a box and a short ID. IDs are numbers, not names.
- As a safety manager, I want every worker marked on the video so that I can see who the system is tracking.
  - [ ] A person on screen gets a box and an ID within a moment of appearing.
  - [ ] A person without a helmet, or without a vest, is flagged as a missing-PPE violation.
  - [ ] A person wearing both is not flagged.

### Danger zone
One fixed red zone is drawn over the video. Its position is set in advance and cannot be moved from the screen.
- As a safety manager, I want to be told when someone is in the danger zone so that I can react.
  - [ ] Someone standing inside the red zone is counted in the "In danger zone" card.
  - [ ] Someone outside the zone is not counted.

### Alerts and siren
- When someone is in the zone, a **red** banner appears across the top of the video panel (for example "Danger zone: 1 worker inside"). When someone is missing a helmet or vest, an **orange** banner appears (for example "PPE missing: 1 without a helmet, 1 without a vest"). The alert is added to the live list in both cases.
- The siren plays while anyone is in the danger zone and stops when the zone is empty. A mute button silences it.
- The live alert list shows the time and what the violation was. Missing-PPE alerts use the yellow/orange accent; danger-zone alerts use red.
- As a safety manager, I want an audible and visible alert so that the danger is noticed immediately.
  - [ ] Entering the zone starts the siren and shows the banner.
  - [ ] Leaving the zone stops the siren and removes the banner.
  - [ ] Pressing mute stops the sound while the banner stays.
  - [ ] Each alert appears in the list with a time and a violation type.

### Counting rules (IDs, two people, re-entry)
- Each person has a worker number ("Worker 1", "Worker 2"...) that starts at 1 in each session. A person only counts after being seen for a few frames, so brief ghost detections are ignored.
- If the system detects the same person twice (for example the face and the upper body), or gives them a new internal ID after a short loss near the same spot, they remain one worker with one number.
- A new zone violation is logged only when a worker **enters** the zone (outside to inside).
- If the same worker leaves the zone and enters again later, it is logged again.
- A missing helmet or vest is logged once per worker per item. It can be logged again only after the worker was seen wearing it for about three seconds in a row and then loses it.
- If the same ID stays in the zone but the system briefly loses and re-detects them, no new violation is logged.
- If two people are in the zone, one siren plays while anyone is inside and each person gets their own log entry. A person who stays inside does not create a new entry on every frame.
- As a safety manager, I want an honest log so that the report can be trusted.
  - [ ] Two people entering the zone produce two log entries and one siren.
  - [ ] One person standing in the zone for a minute produces one entry.
  - [ ] A person who leaves and re-enters produces two entries.

### Event Log and CSV export
- Every incident is saved with a time, a type, and a snapshot image, and is shown in the Event Log table.
- A summary at the top counts incidents by type and shows a compliance figure. It covers the current session only (she cancelled "everything saved"). A monthly average or trend over time belongs to the full product.
- A Download CSV button exports the log (the CSV contains the text columns and the snapshot file names; the images are separate files).
- As a safety manager, I want to review and export incidents so that I can report them to management.
  - [ ] Each alert creates one row with a time, type, and snapshot.
  - [ ] The summary totals equal the number of rows of each type.
  - [ ] Download CSV produces a file that opens in a spreadsheet with the same rows.

## States and Boundaries
- **Empty (nobody in view)** — the video still shows. The cards show real counts (0). The alert list says something like "No alerts, everything is fine". Nothing is invented.
- **Camera or video fails** — the video panel is black and shows the message "Camera unavailable, check the connection" so it is not mistaken for an empty room. The red "recording" dot shows only while a source is live.
- **First use** — opens on the Dashboard, with no login and no setup.
- **Alert active** — banner visible, siren playing unless muted, list updated, "In danger zone" card above zero.
- **Alert resolved** — banner gone, siren stopped.
- **Persistence** — nothing carries over between sessions. Each time the app is opened, the Event Log table, the summary and the counts start empty. Her decision.
- **Privacy** — video stays on the learner's computer. Snapshots may show faces because face blur is deferred.
- **Limit of IDs** — the system may give a person a new ID if it loses them for too long; the counting rules reduce but do not eliminate this.

## Product Decisions
- No login, profile menu, or configuration page — user accounts were cut in scope, and a login adds no value to the demo.
- Two screens only (Dashboard, Event Log) — they are the two things the scope needs.
- Three KPI cards (Workers, Violations, In danger zone); "Safe" is not a card but is counted in the Event Log summary as a compliance figure — her suggestion, so averages live with the report.
- KPI numbers are real counts, never estimates — "we should not invent values".
- Single camera view with a source switch (final), not two tiles at once — keeps the proof of concept small; the recorded clip is also a backup.
- Helmet and hi-vis vest are the PPE items — most reliably detected.
- One shared siren that plays while anyone is in the zone, with a mute button.
- One danger zone only; warning and green zones are later.
- Persons tracked by ID; a new violation counts only on entering the zone — her idea. She suggested using a tracking algorithm (such as SORT) with YOLO to produce the IDs; the technical choice goes to `4-spec`.
- Each session starts with an empty Event Log (option B) — she only wants to see the current session. This replaces her earlier wish for the log to survive a restart. The CSV download is how a session's records can be kept.
- The Event Log summary and the Violations card both cover the current session only; she cancelled the "everything saved" idea.
- Camera-failed message: "Camera unavailable, check the connection".
- Live source is the laptop webcam for now; the DJI Osmo as a live camera is later.
- Palette: greys, deep blue accent, yellow/orange for PPE, red for danger.
- ROI stays in the pitch, not on the dashboard.

## What We're Building
- Login-free app with a top bar, collapsible sidebar, Dashboard and Event Log.
- Source switch: Live (webcam or Osmo) or Recorded (stock or self-filmed clip).
- Person detection with boxes and IDs, and helmet and vest checks.
- One fixed red danger zone drawn over the video.
- Red banner, live alert list, and a siren that plays while someone is in the zone, with mute.
- Three real-count KPI cards.
- Event Log with snapshots, a session summary by type, and CSV download.
- The counting rules for IDs, two people, and re-entry.
- The empty and camera-failed states.

## Deferred From the POC
- Login and user accounts: no value for the demo, and it needs a user store.
- Draggable danger zone: needs an editor; the zone is fixed for now.
- Warning and green zones: more rules and states to show.
- Face blur: extra work; faces may appear in snapshots for now.
- DJI Osmo as a live camera: laptop webcam only for now (an Osmo-filmed clip can still be used as a recorded source).
- Quiet-hours message: needs a schedule.
- Monthly or long-term averages: the demo only runs for minutes.

## Possible Later Enhancements
- CEO summary report with totals by type and zone, trends over time.
- Several cameras at once, with labels and per-zone sirens.
- Gloves and goggles detection, and man-down detection.
- Phone, SMS and Slack alerts; heatmaps and weekly reports.
- A works-council-ready privacy pack for the Netherlands.

## Non-Goals
- No euro or ROI figures on the dashboard: ROI is for the pitch.
- No cloud, multi-site, or user accounts: too much for a day.
- No insurer as a user: a possible later customer.
- No claim that "nobody does this": the research found competitors with PPE detection and siren hardware.

## Open Questions
- Banner position: the bar over the top of the video panel is built (red for the zone, orange for missing PPE). She can still change it.
- Missing-PPE alerts appear in the live list, the banner and the Event Log (option A). She confirmed keeping them all. Resolved.
- Snapshots may show faces (face blur is deferred); she agreed. The public repo must not include snapshot files of real people (use stock or self-filmed footage only).
