# MotionStrike 🥁

MotionStrike is a real-time, camera-based virtual drum kit. No physical drums, no controllers — just your hands or colored sticks in front of a webcam. Drum pads are overlaid directly on the live video feed, and sounds fire the moment you hit them.

---

## How It Works

The app reads your webcam feed, overlays a drum kit layout on screen, and detects when a tracked point (fingertip, wrist, or colored stick tip) enters a pad's bounding box. When a hit is registered, the corresponding drum sound plays instantly via pygame and the pad flashes yellow as visual feedback.

There are two independent tracking modes selectable at launch:

| Mode | Method | Trigger |
|------|--------|---------|
| **Hand Mode** | Google MediaPipe hand skeleton | Index fingertip → all drums; Wrist → Bass |
| **Stick Mode** | HSV color detection | Blue stick → Left hand; Red stick → Right hand |

---

## Drum Layout

Pads are arranged in three rows across a 1280×720 frame:

```
[ HIHAT_CLOSED ]  [ SNARE ]              [ CRASH ]  [ RIDE ]
[ HIHAT_OPEN  ]             [ TOM1 ]  [ TOM2 ]  [ FLOOR_TOM ]
                        [       BASS        ]
```

Each pad has an independent 250 ms cooldown, so hitting one pad never blocks another.

---

## Project Structure

```
MotionStrike/
├── main.py            # Entry point — mode selector
├── hand_tracked.py    # Hand Mode: MediaPipe skeleton tracking
├── sticks.py          # Stick Mode: HSV color tracking
├── drums_engine.py    # Pad layout, sound loading, hit detection, visual flash
├── camera.py          # Cross-platform camera initialisation (macOS / Windows / Linux)
├── sounds/
│   ├── hihat.wav
│   ├── snare.wav
│   ├── tom.wav
│   └── bass.wav
└── test_cam.py        # Quick camera sanity check
```

---

## Requirements

- Python 3.8+
- Webcam (built-in or external)

### Python dependencies

```
opencv-python
mediapipe
pygame
numpy
```

Install everything at once:

```bash
pip install opencv-python mediapipe pygame numpy
```

---

## Running the App

```bash
cd MotionStrike
python main.py
```

You will be prompted to choose a mode:

```
Choose Mode:
1 - Stick Mode
2 - Hand Mode
Enter 1 or 2:
```

Press **`q`** in the video window to quit.

---

## Mode Details

### Hand Mode (`hand_tracked.py`)

Uses **MediaPipe Hands** to detect up to two hands simultaneously.

- The full 21-point hand skeleton is drawn on screen.
- **Index fingertip** (landmark 8) — pink dot — triggers HIHAT_CLOSED, HIHAT_OPEN, SNARE, CRASH, RIDE, TOM1, TOM2, FLOOR_TOM.
- **Wrist** (landmark 0) — orange dot — triggers the BASS pad. Drop your wrist into the bass zone to kick it.
- Handedness (Left / Right label) is correctly resolved after the horizontal camera flip.

### Stick Mode (`sticks.py`)

Uses **HSV color segmentation** to track two colored drum sticks.

- **Blue stick** → mapped to the Left hand
- **Red stick** → mapped to the Right hand

The largest contour above 500 px² is used as the stick tip. Works best with solid-colored stick caps or tape under consistent lighting.

HSV ranges used:

| Stick | Hue range |
|-------|-----------|
| Blue  | 100 – 140 |
| Red   | 0 – 10 and 170 – 180 (wraps around) |

---

<!-- ## Instruments & Sound Files

| Pad | Sound file | Notes |
|-----|-----------|-------|
| HIHAT_CLOSED | `hihat.wav` | |
| HIHAT_OPEN | `hihat.wav` | Swap for open hi-hat sample when available |
| CRASH | `hihat.wav` | Swap for `crash.wav` when available |
| RIDE | `hihat.wav` | Swap for `ride.wav` when available |
| SNARE | `snare.wav` | |
| TOM1 | `tom.wav` | |
| TOM2 | `tom.wav` | |
| FLOOR_TOM | `tom.wav` | |
| BASS | `bass.wav` | |

To add a dedicated sound, drop the `.wav` file into the `sounds/` folder and update the corresponding line in `drums_engine.py`.

--- -->

## Camera Compatibility

`camera.py` handles platform differences automatically:

| OS | Backend |
|----|---------|
| macOS | `cv2.VideoCapture(0)`, falls back to index `1` |
| Windows | `cv2.VideoCapture(0, cv2.CAP_DSHOW)` |
| Linux | `cv2.VideoCapture(0)` |

Default capture resolution is set to **1280×720**.

---

## License

See [LICENSE](LICENSE).

