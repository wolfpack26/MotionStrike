import cv2
import mediapipe as mp
from camera import open_camera
from drums_engine import draw_drums, process_hit

cap = open_camera()

mp_hands = mp.solutions.hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = mp_hands.process(rgb)

    draw_drums(frame)

    if results.multi_hand_landmarks:
        for i, hand in enumerate(results.multi_hand_landmarks):
            h, w, _ = frame.shape
            index_tip = hand.landmark[8]

            cx = int(index_tip.x * w)
            cy = int(index_tip.y * h)

            label = "Left" if i == 0 else "Right"

            cv2.circle(frame, (cx, cy), 8, (255, 0, 255), -1)

            process_hit(label, cx, cy)

    cv2.imshow("MotionStrike", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
