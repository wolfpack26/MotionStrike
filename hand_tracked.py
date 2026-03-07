import cv2
import mediapipe as mp
from camera import open_camera
from drums_engine import draw_drums, process_hit

cap = open_camera()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

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

            # Wrist (landmark 0) triggers BASS
            wrist = hand.landmark[0]
            wx = int(wrist.x * w)
            wy = int(wrist.y * h)

            cv2.circle(frame, (ix, iy), 10, (255, 0, 255), -1)
            cv2.circle(frame, (wx, wy), 8, (255, 180, 0), -1)
            cv2.putText(frame, label, (ix + 15, iy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            process_hit(label, (ix, iy), (wx, wy))

    cv2.imshow("MotionStrike", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
# cv2.destroyAllWindows()
