# SterileView

Touchless intraoperative imaging viewer: scrubbed clinicians browse DICOM
(Digital Imaging and Communications in Medicine) series by gesture without
breaking the sterile field. Sibling project to
[AirSOP](https://github.com/arewa-builds/airsop); same gesture engine
philosophy, different sterile room. Read-only by architecture: there is no
code path that writes to imaging or patient data.

Status: **M0 + M1 complete** (scaffold, capture loop, hand tracking with
EMA-smoothed cursor, HUD with lock banner, headless selfcheck).

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m src.main                  # webcam 0, windowed (ESC quits, L toggles lock)
python -m src.main --synthetic      # no camera? synthetic frames AND hand
python tests/selfcheck.py           # headless checks, no hardware needed
```

## The synthetic pipeline

`SyntheticSource` renders deterministic frames with a moving reticle, and
`SyntheticHandTracker` implements the same interface as the real MediaPipe
tracker while orbiting that reticle with realistic jitter. The full loop
(frame, hands, cursor, HUD) runs with no camera and no GPU, with ground
truth known in advance. In a windowed synthetic run you can watch the
EMA-smoothed cursor trail the reticle exactly the way it should trail a
real hand.

## The lock model

The viewer starts LOCKED every session, renders a full-width banner while
locked, and (at M4) auto-locks after 10 seconds without confident tracking.
In an operating room the system state must be legible from across the room,
and nothing changes state on transient evidence. Until the fist gesture
lands in M2, the `L` key toggles the lock as a dev shortcut.

## M1 exit criterion: the glove check

Landmark quality on gloved hands is the project's biggest technical risk,
so it is tested first, not last. On real hardware: `python -m src.main`,
wear surgical-style gloves, and confirm the cursor tracks smoothly. If it
degrades, the fallback is a coarser wrist-anchor cursor mode. Everything
except this check is covered headless by `tests/selfcheck.py`.

## Repository structure

```
sterileview/
├── README.md
├── PROJECT_PLAN.md         # full end-to-end plan and pipeline
├── requirements.txt
├── data/                   # gitignored; de-identified series only (M3)
├── src/
│   ├── main.py             # capture + hand loop, wiring
│   ├── capture.py          # CameraSource + SyntheticSource
│   ├── hands.py            # HandTracker, SyntheticHandTracker, CursorEMA
│   └── hud.py              # overlay rendering (ViewerState driven)
├── tests/
│   ├── fixtures/           # recorded landmark sequences (M2)
│   └── selfcheck.py        # headless checks
└── assets/
```

## Roadmap

| Milestone | Scope | Exit | Status |
|---|---|---|---|
| M0 | Scaffold, capture, HUD with lock banner | Overlay renders, checks green | done |
| M1 | Hand tracking, EMA cursor | Smooth tracking with gloves | done (glove check on hardware) |
| M2 | Gesture classifier + hold-to-trigger debounce | Fixture replay PASS table | next |
| M3 | DICOM engine: slices, zoom, window/level | Browse a full public CT series | |
| M4 | Lock model + session audit log | Idle auto-lock demo | |
| M5 | Demo video + README strategy section | 60-90 s recorded session | |

Demo content at M3 onward is public, de-identified research data only
(for example The Cancer Imaging Archive). No PHI (Protected Health
Information) ever enters this repository.

## License

MIT (see LICENSE).
