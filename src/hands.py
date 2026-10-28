"""hands.py - hand landmark tracking for SterileView (M1).

HandTracker wraps MediaPipe Hands (lazy import, so headless environments
without mediapipe can still run everything else). SyntheticHandTracker
implements the same interface with deterministic procedural landmarks:
a palm orbiting the synthetic reticle with jitter, so the full loop
(frame -> hands -> cursor -> HUD) runs with no camera and no GPU.

Cursor anchor: the palm center (mean of wrist + four MCP joints) is far
more stable than any fingertip, which is why the cursor anchors there
instead of on the index tip.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# MediaPipe landmark indices used by AirSOP-family gesture code.
WRIST = 0
THUMB_TIP = 4
INDEX_MCP, MIDDLE_MCP, PINKY_MCP = 5, 9, 17
INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP = 8, 12, 16, 20
PALM_JOINTS = (WRIST, INDEX_MCP, MIDDLE_MCP, 13, PINKY_MCP)


@dataclass
class HandObservation:
    """One frame of one hand. landmarks: (21, 3) normalized x, y, z."""
    landmarks: np.ndarray
    handedness: str = "Right"

    @property
    def palm(self) -> np.ndarray:
        """Normalized (x, y) palm center: the cursor anchor."""
        pts = self.landmarks[list(PALM_JOINTS), :2]
        return pts.mean(axis=0)

    def palm_px(self, width: int, height: int) -> tuple[int, int]:
        p = self.palm
        return int(p[0] * width), int(p[1] * height)


class HandTracker:
    """Real hand tracking via MediaPipe. Import is lazy on purpose."""

    def __init__(self, max_num_hands: int = 2,
                 min_detection_confidence: float = 0.6,
                 min_tracking_confidence: float = 0.5):
        try:
            import mediapipe as mp
        except ImportError as e:
            raise RuntimeError(
                "mediapipe is required for live hand tracking; "
                "pip install mediapipe, or run with --synthetic") from e
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence)

    def process(self, frame_bgr: np.ndarray) -> HandObservation | None:
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self._hands.process(rgb)
        if not res.multi_hand_landmarks:
            return None
        lm = res.multi_hand_landmarks[0]
        pts = np.array([[p.x, p.y, p.z] for p in lm.landmark],
                       dtype=np.float64)
        handed = "Right"
        if res.multi_handedness:
            handed = res.multi_handedness[0].classification[0].label
        return HandObservation(landmarks=pts, handedness=handed)

    def close(self) -> None:
        self._hands.close()


class SyntheticHandTracker:
    """Deterministic fake hand: palm orbits the reticle, plus jitter.

    Same interface as HandTracker. Jitter is realistic sensor noise the
    EMA cursor must absorb; the underlying orbit is ground truth.
    """

    # Procedural offsets from palm center for all 21 landmarks, normalized
    # units, roughly an open right palm pointing up. Only coherence matters.
    _POSE = np.array([
        [0.00, 0.06], [-0.03, 0.03], [-0.05, 0.00], [-0.06, -0.02],
        [-0.07, -0.04], [-0.02, -0.03], [-0.02, -0.06], [-0.02, -0.08],
        [-0.02, -0.10], [0.00, -0.03], [0.00, -0.07], [0.00, -0.09],
        [0.00, -0.11], [0.02, -0.03], [0.03, -0.06], [0.03, -0.08],
        [0.03, -0.10], [0.04, -0.02], [0.05, -0.04], [0.06, -0.06],
        [0.06, -0.08]], dtype=np.float64)

    def __init__(self, seed: int = 7, jitter: float = 0.004):
        self.rng = np.random.default_rng(seed)
        self.jitter = jitter
        self._n = 0

    def process(self, frame_bgr: np.ndarray) -> HandObservation:
        t = self._n / 30.0
        c = np.array([0.5 + (1.0 / 3.0) * np.sin(t),
                      0.5 + 0.25 * np.cos(0.7 * t)])
        c = c + self.rng.normal(0.0, self.jitter, 2)
        xy = self._POSE + c
        z = np.zeros((21, 1))
        self._n += 1
        return HandObservation(landmarks=np.hstack([xy, z]))

    def close(self) -> None:
        pass


class CursorEMA:
    """Exponential moving average cursor smoother.

    alpha trades responsiveness against jitter rejection: 0.4 settles in
    roughly five frames while absorbing landmark noise. First observation
    initializes the cursor directly, no ramp-in.
    """

    def __init__(self, alpha: float = 0.4):
        self.alpha = alpha
        self._p: np.ndarray | None = None

    def update(self, point: np.ndarray) -> np.ndarray:
        point = np.asarray(point, dtype=np.float64)
        if self._p is None:
            self._p = point
        else:
            self._p = self.alpha * point + (1.0 - self.alpha) * self._p
        return self._p

    @property
    def value(self) -> np.ndarray | None:
        return self._p
