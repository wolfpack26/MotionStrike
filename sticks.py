import cv2
import numpy as np
import pygame
import time
from camera import open_camera

pygame.mixer.init()

cap = open_camera()

# Drum pad definitions (x1, y1, x2, y2)
DRUMS = {
    "SNARE": (50, 50, 250, 200),
    "HIHAT": (300, 50, 500, 200),
    "BASS":  (550, 50, 750, 200),
}

SOUNDS = {
    "SNARE": pygame.mixer.Sound("sounds/snare.wav"),
    "HIHAT": pygame.mixer.Sound("sounds/hihat.wav"),
    "BASS":  pygame.mixer.Sound("sounds/bass.wav"),
}

HIT_COOLDOWN = 0.25  # seconds
last_hit_time = {
    "Blue": 0,
    "Red": 0
}

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

def is_inside(cx, cy, drum):
    x1, y1, x2, y2 = drum
    return x1 < cx < x2 and y1 < cy < y2
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ---------------- DRAW DRUM PADS ----------------
    for drum, (x1, y1, x2, y2) in DRUMS.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, drum, (x1 + 10, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # ---------------- BLUE STICK ----------------
    blue = detect_color(hsv, BLUE_LOWER, BLUE_UPPER)
    if blue:
        x, y, w, h, cx, cy = blue
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
        cv2.putText(frame, "Blue Stick", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        for drum_name, drum_area in DRUMS.items():
            if is_inside(cx, cy, drum_area):
                current_time = time.time()
                if current_time - last_hit_time["Blue"] > HIT_COOLDOWN:
                    SOUNDS[drum_name].play()
                    last_hit_time["Blue"] = current_time


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

            for drum_name, drum_area in DRUMS.items():
                if is_inside(cx, cy, drum_area):
                    current_time = time.time()
                    if current_time - last_hit_time["Red"] > HIT_COOLDOWN:
                        SOUNDS[drum_name].play()
                        last_hit_time["Red"] = current_time


    cv2.imshow("Two Stick Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
#cv2.destroyAllWindows()