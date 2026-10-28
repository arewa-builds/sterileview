# SterileView Demo Script (M5 deliverable)

Target: 60 to 90 seconds, 1080p, screen capture with the live webcam feed
visible (picture-in-picture of the gesturing hand sells "touchless" better
than any narration). This video is the final task of the project and the
LinkedIn posting artifact. Every milestone before it exists to make these
90 seconds possible.

## Shot list

| Time | Shot | Narration |
|---|---|---|
| 0-5 s | Title card: "SterileView: touchless imaging for the sterile field" over a gloved hand held near a keyboard it cannot touch | None. Let the image explain itself. |
| 5-15 s | Gloved hands, tray, monitor across the room | "A scrubbed clinician cannot touch a workstation. Today that means describing slices to a circulator nurse, or breaking scrub and re-gowning." |
| 15-25 s | App boots. HUD renders. LOCKED banner full width | "SterileView starts locked. Every session. Nothing in this room changes state by accident." |
| 25-35 s | Fist hold, banner clears, cursor arms teal | "A deliberate fist hold unlocks it. Sustained intent, never a transient." |
| 35-70 s | Core run: pinch scrolls slices, two-hand spread zooms, wrist rotate adjusts window/level, swipe changes series. Gesture chip confirms each fire | "Pinch grabs the stack. Two hands zoom. A wrist rotation is window and level. Swipe moves between series. No keyboard, no mouse, no broken field." |
| 70-80 s | Hands drop out of frame; idle; auto-LOCK banner returns | "Step away, and it locks itself." |
| 80-90 s | Session audit log scrolls; end card with repo URL | "Every gesture is logged. The viewer is read-only by architecture: there is no code path that writes to the patient record." |

## Recording notes

- Record at 1920x1080; the HUD text must be legible on a phone screen,
  because that is where LinkedIn plays it.
- Two full takes minimum; the second is almost always the keeper.
- Narration can be voiceover in post or silent with caption cards; decide
  after take one. Silent-plus-captions survives muted autoplay better.
- Wear the gloves in every shot. The gloves are the whole point.
- The auto-lock beat (70-80 s) is the clip most likely to be rewatched;
  do not cut it for time.

## LinkedIn post copy (draft)

Hook: "A surgeon mid-case cannot touch a keyboard. So I built an imaging
viewer that does not have one."

Body: "SterileView lets a scrubbed clinician browse DICOM studies with
hand gestures: pinch to scroll slices, two hands to zoom, a wrist turn for
window/level. It starts locked every session, auto-locks when you step
away, and it is read-only by architecture. Built with Python, OpenCV, and
MediaPipe. Full repo and writeup in the comments."

Tags: #MedicalImaging #ComputerVision #DigitalHealth #MedTech

## What this script demands from the build

- M2 gestures must fire visibly on the gesture chip within one frame of
  trigger; hesitation reads as broken on video.
- M3 viewer must preload the demo series; no loading spinners on camera.
- M4 auto-lock must trigger cleanly at the 10-second mark; rehearse the
  hands-out-of-frame beat.
- The audit log scroll at the end requires M4's log to be human-legible,
  not just machine-parseable.
