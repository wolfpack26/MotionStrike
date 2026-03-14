# MotionStrike 🥁

MotionStrike is a real-time, camera-based virtual drum kit. No physical drums, no controllers — just your hands or colored sticks in front of a webcam. Drum pads are overlaid directly on the live video feed, and sounds fire the moment you hit them.

---

## How It Works

The app reads your webcam feed, overlays a drum kit layout on screen, and detects when a tracked point (fingertip, thumb, or colored stick tip) enters a pad's bounding box. When a hit is registered, the corresponding drum sound plays instantly via pygame and the pad flashes yellow as visual feedback.

There are two independent tracking modes selectable at launch:

| Mode | Method | Trigger |
|------|--------|---------|
| **Hand Mode** | Google MediaPipe hand skeleton | Index fingertip → all drums; thumb → Bass |
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
│   ├── closed_hihat.wav
│   ├── open_hihat.wav
│   ├── crash_cymbal.wav
│   ├── hihat.wav
│   ├── snare.wav
│   ├── high_tom.wav
│   ├── mid_tom.wav
│   ├── floor_tom.wav
│   └── bass.wav
└── test_cam.py        # Quick camera sanity check
```

---

## Requirements

- Python 3.8+
- Recommended: Python 3.11 or 3.12
- Webcam (built-in or external)

### Python dependencies

```
opencv-python
mediapipe==0.10.9
pygame
numpy
```

Install everything at once:

```bash
pip install opencv-python mediapipe==0.10.9 pygame numpy
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
- **Index fingertip** (landmark 8) — pink dot — triggers HIHAT_CLOSED, HIHAT_OPEN, SNARE, CRASH, RIDE, HIGH TOM, MID TOM, FLOOR_TOM.
- **thumb** (landmark 4) — blue dot — triggers the BASS pad. Drop your thumb into the bass zone to kick it.
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

To use custom samples, replace files in `sounds/` with your own `.wav` files or update the pad mapping in `drums_engine.py`.

---

## Camera Compatibility

`camera.py` handles platform differences automatically:

| OS | Backend |
|----|---------|
| macOS | `cv2.VideoCapture(1)`, use index '0' for Continuity Camera |
| Windows | `cv2.VideoCapture(0, cv2.CAP_DSHOW)` |
| Linux | `cv2.VideoCapture(0)` |

Default capture resolution is set to **1280×720**.

---

## Contributing

Contributions are welcome and appreciated.

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and test locally (`python main.py`).
4. Commit with a clear message.
5. Open a Pull Request describing what changed and why.

If you are adding new sounds or changing pad behavior, please include a short demo clip or screenshots in your PR when possible.

---

## License

See [LICENSE](LICENSE).

