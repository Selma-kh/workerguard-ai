---
doc: scope
status: approved
---

# Worker Safety AI

Working title. Name candidates: Third Eye, Worker Safe, Safe AI (to pick before shipping).

A computer-vision safety layer that detects workers on video, flags missing PPE and danger-zone entry, sounds an alert, and shows it all to a safety manager on a dashboard.

## The Unique Kernel
Detection to action with no new hardware and privacy by default: when a worker is missing PPE or enters a danger zone, the system sounds a siren and records the incident (event log with snapshot, CSV export), so detection turns into an on-site response and not just a dashboard number. It works on cameras a site already has and keeps video on-site.

Honest note from the research: none of these is unique on its own. Intenseye sells siren/beacon hardware, Protex AI says it can drive PLCs and safety hardware, and Protex and Visionify already stress privacy and "no new cameras". The distinctive part is the combination for sites that cannot buy enterprise hardware. Selma also considered a Dutch works-council-ready angle (consent under WOR Art. 27, DPIA pack) and decided to keep the market open, not limited to the Netherlands, so that angle is optional for now. Pitch carefully: do not claim "nobody does this".

Market: open and not limited to one country. The Netherlands/Europe remains the reference example (ROI numbers come from there).

## Who It's For
The HSE (health, safety and environment) manager of an industrial site. Today they rely on weekly walk-around audits, so 167 of 168 hours go unmonitored, and they only learn about incidents after workers are hurt. The company owner and insurer care about the ROI, but they are not the day-to-day user.

## The Core Loop
The HSE manager opens the dashboard. It shows the camera view with detected workers, a danger zone drawn over the floor, and a live list of violations. When a worker is missing PPE or steps into the zone, a siren sounds, a red banner appears, and the event is added to the list. They come back to see how many workers are safe and how many are in danger.

## Inspiration & Identity
Reference design: her mock dashboard, https://safe-watch-demo.lovable.app/worker-safety-ai.html (status cards, camera tiles, compliance by zone, danger-zone panel). Her own sales deck, "Worker Safety AI Internal Sales Training (Blue Edition)", sets the blue visual identity. Competitors referenced: Intenseye, Voxel, Protex AI.

## Why This Matters to the Learner
A worker-safety product that pairs computer vision with a business case based on the cost of workplace injuries.

## What "Working" Looks Like
A one-minute demo: a video (freely licensed stock footage, or staged clips from her webcam / DJI Osmo) plays on the dashboard. A worker is detected with boxes drawn on them. When the worker lacks a helmet or vest, or walks into the fixed red danger zone, the siren sounds, a red banner appears, and the violations count and alert list update. ROI (about €75K per injury in the Netherlands against about €25K per year for the platform) is shown in her narration and pitch, not in the dashboard.

## The POC Boundary
- One camera view on the dashboard at a time, with a source switch: Live (laptop webcam, or the DJI Osmo if it works as a live camera) or Recorded (a freely licensed stock clip, not YouTube, or a clip she films). Not several cameras at once.
- Detect people and two PPE items: helmet and hi-vis vest.
- One fixed danger zone drawn over the video (coordinates set in advance, not dragged).
- Alert: siren sound on the laptop plus a red banner. If two people are in the zone, one siren plays while anyone is inside, with one log entry per person (no repeat entries for someone who stays in the zone).
- One dashboard page: workers detected, violations, live alert list.
- Event log: every alert is saved with time, camera, type and a snapshot image, and shown in a table.
- CSV export of the event log (Selma's idea). It is the stopgap "report" for managers or the CEO.

## Later
- CEO summary report (totals by type and zone, trends) built from the event log.
- Per-zone alerts, labels and different sounds/lights when there are several cameras and sirens.
- Multiple cameras and zones; CCTV/RTSP integration and an edge box.
- Phone, SMS and Slack notifications.
- Gloves and goggles detection.
- Man-down and fall detection.
- Face blurring.
- Risk heatmaps and weekly HSE reports.
- Draggable danger zone.

## Explicitly Cut
- Euro/ROI figures on the dashboard: ROI is for the pitch and the insurer story, not a dashboard feature.
- Cloud layer, multi-site, and user accounts: too much for a day, and not needed to prove the kernel.
- Pricing, sales motion, roadmap and GDPR kit as product features: they stay in the pitch deck.
- A single-country focus: Selma wants the market kept open. Note: the Gulf (Dubai, Qatar) was researched and is already served by viAct, Invigilo and AvidBeam, so it is not a priority.
- Insurer as a user: a possible later customer, not needed for the proof of concept.
