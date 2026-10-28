"""main.py - SterileView capture + hand loop (M0 + M1).

Usage:
    python -m src.main                 # webcam 0, windowed (ESC quits, L toggles lock)
    python -m src.main --synthetic     # synthetic frames + synthetic hand
    python -m src.main --synthetic --headless --frames 90   # smoke run

M1 cursor: palm-center landmark, EMA smoothed, rendered by the HUD.
Dev shortcut: L toggles the lock state until the fist gesture (M2) owns it.
"""
from __future__ import annotations

import argparse

import cv2

from .capture import CameraSource, SyntheticSource, FpsCounter
from .hands import HandTracker, SyntheticHandTracker, CursorEMA
from .hud import ViewerState, draw_hud


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="sterileview")
    p.add_argument("--camera", type=int, default=0)
    p.add_argument("--synthetic", action="store_true",
                   help="deterministic synthetic frames and hand")
    p.add_argument("--headless", action="store_true",
                   help="no window; run --frames frames and exit")
    p.add_argument("--frames", type=int, default=90)
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.synthetic:
        source = SyntheticSource(args.width, args.height)
        tracker = SyntheticHandTracker()
    else:
        source = CameraSource(args.camera, args.width, args.height)
        tracker = HandTracker()

    fps = FpsCounter()
    cursor = CursorEMA(alpha=0.4)
    state = ViewerState()
    shown = 0
    try:
        while True:
            ok, frame = source.read()
            if not ok:
                break
            obs = tracker.process(frame)
            if obs is not None:
                p = cursor.update(obs.palm)
                state.cursor = (int(p[0] * frame.shape[1]),
                                int(p[1] * frame.shape[0]))
            state.fps = fps.tick()
            draw_hud(frame, state)
            shown += 1

            if args.headless:
                if shown >= args.frames:
                    break
            else:
                cv2.imshow("SterileView", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:                      # ESC
                    break
                if key in (ord("l"), ord("L")):    # dev lock toggle
                    state.locked = not state.locked
    finally:
        source.release()
        tracker.close()
        if not args.headless:
            cv2.destroyAllWindows()

    print(f"frames={shown}  achieved_fps={state.fps:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
