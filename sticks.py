import cv2
import numpy as np
import pygame
from camera import open_camera
from drums_engine import draw_drums, process_hit

pygame.mixer.init()

cap = open_camera()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow("MotionStrike", cv2.WINDOW_NORMAL)
cv2.resizeWindow("MotionStrike", 1280, 720)

# HSV ranges
BLUE_LOWER = np.array([100, 150, 50])
BLUE_UPPER = np.array([140, 255, 255])

RED_LOWER1 = np.array([0, 150, 50])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([170, 150, 50])
RED_UPPER2 = np.array([180, 255, 255])

def detect_color(frame, lower, upper):
    mask = cv2.inRange(frame, lower, upper)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + w // 2, y + h // 2
            return (x, y, w, h, cx, cy)
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ---------------- DRAW DRUM PADS ----------------
    draw_drums(frame)

    # ---------------- BLUE STICK ----------------
    blue = detect_color(hsv, BLUE_LOWER, BLUE_UPPER)
    if blue:
        x, y, w, h, cx, cy = blue
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
        cv2.putText(frame, "Blue Stick", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        process_hit("Left", cx, cy)

    # ---------------- RED STICK ----------------
    mask1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
    mask2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
    red_mask = mask1 | mask2

    contours, _ = cv2.findContours(
        red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + w // 2, y + h // 2

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, "Red Stick", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            process_hit("Right", cx, cy)

    cv2.imshow("MotionStrike", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
# cv2.destroyAllWindows()
