import cv2
import math
import time
from collections import deque
import mediapipe as mp
from camera import open_camera
from drums_engine import draw_drums, process_hit, DEBUG_Z

cap = open_camera()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
    model_complexity=0 
)
mp_draw = mp.solutions.drawing_utils

# Position history buffers per hand: entries are (x, y, timestamp)
position_history = {"Left": deque(maxlen=3), "Right": deque(maxlen=3)}
thumb_history    = {"Left": deque(maxlen=3), "Right": deque(maxlen=3)}

def compute_velocity(history):
    """Return (velocity px/s, dy) using oldest and newest buffer entries."""
    if len(history) < 2:
        return 0.0, 0
    x1, y1, t1 = history[0]
    x2, y2, t2 = history[-1]
    dt = t2 - t1
    if dt == 0:
        return 0.0, 0
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    # Use only the last two frames for direction — prevents tap+bounce cancelling to 0
    _, prev_y, _ = history[-2]
    _, cur_y,  _ = history[-1]
    dy = cur_y - prev_y
    return d / dt, dy

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    draw_drums(frame)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            h, w, _ = frame.shape

            # Draw the full hand skeleton
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # MediaPipe handedness is flipped after cv2.flip, so swap the label
            raw_label = handedness.classification[0].label
            label = "Right" if raw_label == "Left" else "Left"

            # Index fingertip (landmark 8) triggers all drums except BASS
            index = hand.landmark[8]
            ix = int(index.x * w)
            iy = int(index.y * h)
            index_z = index.z

            # thumb (landmark 4) triggers BASS
            thumb = hand.landmark[4]
            wx = int(thumb.x * w)
            wy = int(thumb.y * h)

            # Update position history and compute velocity + direction
            now = time.time()
            position_history[label].append((ix, iy, now))
            thumb_history[label].append((wx, wy, now))
            tip_vel,   tip_dy   = compute_velocity(position_history[label])
            thumb_vel, thumb_dy = compute_velocity(thumb_history[label])

            cv2.circle(frame, (ix, iy), 10, (255, 0, 255), -1)
            cv2.circle(frame, (wx, wy), 8, (255, 180, 0), -1)
            cv2.putText(frame, label, (ix + 15, iy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            if DEBUG_Z:
                cv2.putText(frame, f"z={index_z:.3f}", (ix + 15, iy + 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)
                cv2.putText(frame, f"v={tip_vel:.0f}px/s", (ix + 15, iy + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)

            process_hit(label, (ix, iy), (wx, wy),
                        velocity=tip_vel, dy=tip_dy, index_z=index_z,
                        thumb_velocity=thumb_vel, thumb_dy=thumb_dy)

    cv2.imshow("MotionStrike", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
# cv2.destroyAllWindows()
