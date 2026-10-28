"""selfcheck.py - M0 + M1 headless checks.

Usage: python3 tests/selfcheck.py   (from the repo root)

Fixtures over cameras: everything here runs without hardware and without
mediapipe (the real tracker imports lazily; the synthetic one covers the
loop). The live glove check happens on real hardware; see README.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.capture import SyntheticSource, FpsCounter            # noqa: E402
from src.hands import SyntheticHandTracker, HandObservation, CursorEMA  # noqa: E402
from src.hud import ViewerState, draw_hud                      # noqa: E402
from src.main import main                                      # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name:<42} {detail}")


def t_synthetic_frames():
    src = SyntheticSource(640, 360)
    ok, frame = src.read()
    check("synthetic frame shape/dtype",
          ok and frame.shape == (360, 640, 3) and frame.dtype == np.uint8,
          str(frame.shape))
    a = SyntheticSource(320, 240).read()[1]
    b = SyntheticSource(320, 240).read()[1]
    check("synthetic source deterministic", np.array_equal(a, b))


def t_synthetic_hand():
    h1, h2 = SyntheticHandTracker(), SyntheticHandTracker()
    seq1 = [h1.process(np.zeros((4, 4, 3), np.uint8)).palm for _ in range(10)]
    seq2 = [h2.process(np.zeros((4, 4, 3), np.uint8)).palm for _ in range(10)]
    same = all(np.allclose(p, q) for p, q in zip(seq1, seq2))
    check("synthetic hand deterministic", same)

    obs = SyntheticHandTracker().process(np.zeros((4, 4, 3), np.uint8))
    good = (obs.landmarks.shape == (21, 3)
            and np.all(obs.palm >= 0.0) and np.all(obs.palm <= 1.0))
    check("observation: 21 landmarks, palm normalized", good,
          f"palm={obs.palm.round(3)}")


def t_palm_anchor_and_pixels():
    lm = np.zeros((21, 3))
    lm[[0, 5, 9, 13, 17], :2] = 0.5      # palm joints at center
    lm[8, :2] = 0.9                       # index tip far away: must NOT move palm
    obs = HandObservation(landmarks=lm)
    px = obs.palm_px(640, 360)
    check("cursor anchors to palm center, not fingertip",
          np.allclose(obs.palm, 0.5) and px == (320, 180), str(px))


def t_ema_smoothing():
    rng = np.random.default_rng(7)
    target = np.array([0.5, 0.5])
    raw = target + rng.normal(0.0, 0.01, (60, 2))
    cur = CursorEMA(alpha=0.4)
    out = np.array([cur.update(p) for p in raw])
    check("EMA reduces jitter",
          out[20:].std() < raw[20:].std(),
          f"raw std {raw[20:].std():.4f} -> smooth {out[20:].std():.4f}")
    check("EMA converges to target",
          np.all(np.abs(out[-1] - target) < 0.01),
          f"final={out[-1].round(4)}")


def t_hud_and_lock_banner():
    frame = SyntheticSource(640, 360).read()[1]
    unlocked = frame.copy()
    draw_hud(unlocked, ViewerState(locked=False, cursor=(320, 180), fps=30))
    locked = frame.copy()
    draw_hud(locked, ViewerState(locked=True, cursor=(320, 180), fps=30))
    diff = int(np.count_nonzero(unlocked != locked))
    check("HUD renders; lock banner changes the frame",
          diff > 1000, f"{diff} px differ")


def t_headless_loop():
    rc = main(["--synthetic", "--headless", "--frames", "60",
               "--width", "640", "--height", "360"])
    check("headless capture+hand loop, 60 frames", rc == 0)


def t_fps_pacing():
    src = SyntheticSource(640, 360, fps=30.0)
    fps = FpsCounter()
    for _ in range(60):
        src.read()
        m = fps.tick()
    check("synthetic pacing near 30 fps", m >= 15.0, f"{m:.1f} fps")


if __name__ == "__main__":
    t_synthetic_frames()
    t_synthetic_hand()
    t_palm_anchor_and_pixels()
    t_ema_smoothing()
    t_hud_and_lock_banner()
    t_headless_loop()
    t_fps_pacing()
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks PASS")
    sys.exit(0 if all(RESULTS) else 1)
