# SterileView: Touchless Intraoperative Imaging Viewer

End-to-end plan and pipeline for a computer-vision interaction layer that
lets scrubbed clinicians browse medical imaging hands-free in the operating
room: gesture navigation of DICOM (Digital Imaging and Communications in
Medicine) series, a deliberate lock model so nothing happens without
sustained intent, and a session audit log. Sibling project to AirSOP; same
gesture engine, different sterile room.

Name: SterileView (confirmed).

---

## Why this project exists

A surgeon mid-procedure cannot touch a PACS (Picture Archiving and
Communication System) workstation without breaking the sterile field. The
current workarounds are asking a circulator nurse to click through scans by
verbal instruction, or breaking scrub and re-gowning, which costs the room
ten or more minutes each time. SterileView demonstrates the alternative: the
surgeon gestures in the air to scroll slices, zoom, pan, and adjust
window/level, while the system stays read-only by design and locks itself
the moment attention drops.

Career alignment: this is the medtech counterpart to AirSOP's lab story.
Together they form a family of touchless sterile-environment interfaces,
which is exactly the AI and computer-vision medtech track on the resume.
It complements SurgicalVision rather than overlapping it: SurgicalVision
coaches trainees in simulation; SterileView serves the live workflow.

## Success definition

- Public GitHub repo running end to end on a laptop with a webcam.
- 60 to 90 second demo video: a full imaging session browsed by gesture,
  including the lock engaging on an idle timeout.
- README with a director-level strategy section: pilot setting, metrics,
  integration path, regulatory framing.

## System pipeline

```
webcam
  └─► capture loop (OpenCV, 30 fps target)
        ├─► hand tracking (MediaPipe Hands, 21 landmarks per hand)
        │     └─► gesture classifier (geometric rules on landmarks)
        │           └─► debouncer (hold-to-trigger state machine)
        │                 └─► gesture events (GRAB, SWIPE, SPREAD, LOCK)
        ├─► DICOM engine (pydicom: series, slices, window/level presets)
        ▼
  viewer state (series, slice, zoom, pan, window/level, lock)
        ├─► HUD overlay (slice info, gesture state, lock banner)
        └─► session audit log (view-only events, no PHI stored)
```

Read-only is architectural, not a disclaimer: the viewer never writes back
to the imaging data or any patient record. The only persistence is the
session audit log, which records what was viewed and which gestures fired.

## Gesture vocabulary

Same engine as AirSOP, retuned for imaging. Geometric rules only, no
trained model, every rule explainable in a clinical review.

| Gesture | Mapping | Trigger |
|---|---|---|
| Open palm | Cursor hover | Continuous (EMA smoothed) |
| Pinch hold, move vertically | Scroll through slices | Hold 5 frames |
| Two-hand spread or close | Zoom in or out | Continuous |
| Pinch hold, rotate wrist | Window/level adjust | Hold 5 frames |
| Swipe left or right | Next or previous series | Velocity plus hold |
| Fist hold | LOCK or unlock the viewer | Hold 8 frames |

## The lock model (the OR difference)

In a lab, a false gesture wastes a step. In an operating room, a false
gesture during a critical moment is a different class of problem, so the
safety model leads the design:

- Viewer starts LOCKED every session. Unlocking requires the deliberate
  fist hold; there is no accidental path to an active cursor.
- Auto-lock after 10 seconds with no confident hand tracking.
- LOCKED state renders a full-width banner so the whole room can see the
  system state at a glance.
- This is the same hysteresis philosophy as the robot debouncer and the
  AirSOP gesture stabilizer: nothing changes state on transient evidence.

## DICOM engine

- pydicom loads a series directory; slices sorted by instance number and
  verified against slice position.
- Pixel pipeline: rescale to Hounsfield units where present, then
  window/level mapping to 8-bit display, with named presets (lung, bone,
  soft tissue, brain) selectable by gesture.
- Zoom and pan applied at render time; source pixels never mutated.
- Demo content: public, de-identified research series only (for example
  The Cancer Imaging Archive or pydicom sample data). No PHI (Protected
  Health Information) ever enters the repo; datasets are gitignored.

## Repository structure

```
sterileview/
├── README.md               # story, demo gif, strategy section
├── PROJECT_PLAN.md
├── requirements.txt        # opencv-python, mediapipe, numpy, pydicom
├── data/                   # gitignored; de-identified series only
├── src/
│   ├── main.py             # capture loop and wiring
│   ├── capture.py          # CameraSource + SyntheticSource
│   ├── hands.py            # MediaPipe wrapper (M1)
│   ├── gestures.py         # rule-based classifier (M2)
│   ├── debouncer.py        # hold-to-trigger state machine (M2)
│   ├── dicom_view.py       # series loading, slice render, W/L (M3)
│   ├── lockout.py          # lock state machine (M4)
│   ├── audit.py            # session event log (M4)
│   └── hud.py              # overlay rendering
├── tests/
│   ├── fixtures/           # recorded landmark sequences per gesture
│   └── selfcheck.py        # headless checks, no hardware
└── assets/
```

## Family architecture

M2 is the decision point for the shared core: gestures, debouncer, capture,
and HUD are byte-identical in spirit to AirSOP's. The pragmatic path is
duplicate now, extract a small shared package (working name airgesture)
once both gesture vocabularies are stable, and let both repos depend on it.
Do not pay for the abstraction before the second use case is real; at M2
it becomes real.

## Milestones and exit criteria

### M0: scaffold and capture (day 1)
Repo, camera loop, HUD skeleton with lock banner placeholder, synthetic
source, headless selfcheck. Exit: overlay renders, checks green.

### M1: hands and cursor (days 2 to 3)
Landmarks streaming, EMA (Exponential Moving Average) cursor. Exit:
smooth tracking while wearing surgical-style gloves, not just bare hands.

### M2: gestures and debounce (days 4 to 6)
Classifier for the six gestures, hold-to-trigger, recorded fixtures,
fixture-replay selfcheck. Exit: gesture logic verified with no camera.
Extract shared core if both vocabularies are stable.

### M3: DICOM engine and viewer (days 7 to 10)
Series loading, slice navigation, zoom and pan, window/level presets, all
driven by gesture events. Exit: browse a full public CT (Computed
Tomography) series start to finish without touching the keyboard.

### M4: lock model and audit (days 11 to 12)
Deliberate unlock, 10-second idle auto-lock, lock banner, session audit
log of view events. Exit: scripted demo shows lock engaging on idle and a
log that replays the session.

### M5: polish and launch (days 13 to 15)
Demo script rehearsed, video recorded, README strategy section, LinkedIn
post drafted. Exit: 60 to 90 second video of a complete session.

Roughly three weeks part-time, parallel to AirSOP's later milestones if
desired, since the M0 to M2 patterns are already proven there.

## Testing philosophy

Fixtures over cameras, identical to AirSOP: recorded landmark sequences
replayed against the classifier deterministically. DICOM engine gets unit
tests on public sample data: slice ordering, Hounsfield rescale, and
window/level math checked against known values. Deterministic inputs,
ground truth known in advance.

## Strategy section content (for the README)

- **Pilot setting:** a simulation center or anatomy teaching lab, not a
  live OR. Honest about the gap between demo and clinical deployment.
- **Metrics:** scrub breaks avoided per session, time-to-image versus the
  circulator-nurse workflow, gesture accuracy on fixtures.
- **Integration path:** the viewer reads DICOM, so any PACS can be a
  source; the audit log maps to access-review expectations under HIPAA
  (Health Insurance Portability and Accountability Act).
- **Regulatory framing:** workflow assistance, read-only, never diagnostic
  support. A diagnostic-capable future would enter IEC 62304
  (International Electrotechnical Commission standard 62304) software
  lifecycle territory and FDA (Food and Drug Administration) review; the
  README says so plainly, which is the answer a director wants to hear.

## Risks and mitigations

- **Gloved and occluded hands.** Surgical gloves plus fluids are the hard
  case; the glove test lands in M1, and a coarse wrist-cursor mode is the
  fallback.
- **Dataset sourcing.** Public de-identified series only, documented in
  the README with links; nothing patient-derived is committed.
- **Scope creep into instrument counting.** Retained-item prevention is a
  real patient-safety problem and a tempting stretch; it stays a stretch
  until the viewer ships.
- **Overclaiming clinical readiness.** Every public artifact frames this
  as a workflow interface demonstrated on research data, never a clinical
  device.

## Resume and LinkedIn integration

Resume line for the medtech track: "Built SterileView, a touchless DICOM
viewer for sterile environments (Python, OpenCV, MediaPipe, pydicom):
gloved clinicians browse imaging by gesture while a lockout state machine
and session audit keep the system read-only and intent-driven."

Family narrative for interviews: "I built a pair of touchless interfaces
for sterile environments. AirSOP digitizes the lab bench protocol;
SterileView keeps the surgeon in the sterile field while they read imaging.
Same engine, two rooms, one thesis: hands that must stay clean should
never touch a keyboard."

## Interview sound bites

- "Read-only is architecture, not a disclaimer. The system cannot write to
  the patient record because there is no code path that writes."
- "The lock model is the OR analog of the robot debouncer: state changes
  require sustained intent, never a transient."
- "M2 is where I would extract the shared gesture core, because that is
  the moment the second use case makes the abstraction honest."
