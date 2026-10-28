"""hud.py - heads-up display overlay for SterileView.

M0/M1 chrome: banner, viewer placeholders (series/slice/window-level fill
in at M3), gesture chip, footer, and the lock banner. The lock banner is
full width on purpose: in an OR, the system state must be legible from
across the room, not just to the person gesturing.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

FONT = cv2.FONT_HERSHEY_SIMPLEX
INK = (235, 235, 235)              # BGR
MUTED = (150, 150, 150)
PANEL = (24, 24, 24)
ARMED = (200, 160, 40)             # teal-ish accent, cursor when unlocked
LOCKED = (60, 60, 200)             # red-ish, everything lock-related


@dataclass
class ViewerState:
    """Everything the overlay is allowed to know. Defaults = M0/M1."""
    series: str = "--"
    slice_index: int | None = None
    slice_count: int | None = None
    wl_preset: str = "--"
    gesture: str = "--"
    fps: float = 0.0
    locked: bool = True              # viewer starts LOCKED every session
    cursor: tuple[int, int] | None = None


def _panel(frame, x0, y0, x1, y1, alpha=0.65):
    roi = frame[y0:y1, x0:x1]
    fill = np.full_like(roi, PANEL)
    frame[y0:y1, x0:x1] = cv2.addWeighted(fill, alpha, roi, 1 - alpha, 0)


def _text(frame, text, org, scale=0.6, color=INK, thickness=1):
    cv2.putText(frame, text, org, FONT, scale, color, thickness, cv2.LINE_AA)


def draw_hud(frame: np.ndarray, state: ViewerState) -> np.ndarray:
    """Draw the overlay in place and return the frame."""
    h, w = frame.shape[:2]

    # top banner
    _panel(frame, 0, 0, w, 56)
    _text(frame, "STERILEVIEW", (16, 38), 0.9, INK, 2)
    _text(frame, "touchless intraoperative imaging viewer", (220, 38),
          0.6, MUTED)

    # lock banner: full width, impossible to miss
    if state.locked:
        _panel(frame, 0, 60, w, 96, alpha=0.8)
        _text(frame, "LOCKED - hold fist to unlock", (16, 88), 0.7,
              LOCKED, 2)
        _text(frame, "(fist gesture lands in M2; dev key L toggles)",
              (w - 470, 88), 0.5, MUTED)

    # viewer panel (left): M3 fills these from the DICOM engine
    _panel(frame, 12, 112, 360, 232)
    _text(frame, f"series: {state.series}", (28, 148), 0.6, MUTED)
    if state.slice_index is None:
        _text(frame, "slice:  -- / --", (28, 180), 0.6, MUTED)
    else:
        _text(frame, f"slice:  {state.slice_index} / {state.slice_count}",
              (28, 180), 0.6, INK)
    _text(frame, f"window: {state.wl_preset}", (28, 212), 0.6, MUTED)

    # status chips (right)
    _panel(frame, w - 268, 112, w - 12, 208)
    _text(frame, f"gesture: {state.gesture}", (w - 252, 148), 0.55, INK)
    mode = "disarmed" if state.locked else "armed"
    _text(frame, f"cursor:  {mode}", (w - 252, 180), 0.55,
          LOCKED if state.locked else ARMED)

    # cursor: amber ring when disarmed, accent when armed
    if state.cursor is not None:
        cx, cy = state.cursor
        color = LOCKED if state.locked else ARMED
        cv2.circle(frame, (cx, cy), 18, color, 2, cv2.LINE_AA)
        cv2.drawMarker(frame, (cx, cy), color, cv2.MARKER_CROSS, 20, 2,
                       cv2.LINE_AA)

    # footer
    _panel(frame, 0, h - 44, w, h)
    _text(frame, f"{state.fps:4.1f} fps", (16, h - 15), 0.55, MUTED)
    _text(frame, f"{w}x{h}", (130, h - 15), 0.55, MUTED)
    _text(frame, "M0+M1", (w - 110, h - 15), 0.55, ARMED)
    return frame
