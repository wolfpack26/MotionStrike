import pygame
import time

pygame.mixer.init()

SOUNDS = {
    # Top row
    "HIHAT_CLOSED": pygame.mixer.Sound("sounds/hihat.wav"),
    "SNARE":        pygame.mixer.Sound("sounds/snare.wav"),
    "CRASH":        pygame.mixer.Sound("sounds/hihat.wav"),
    "RIDE":         pygame.mixer.Sound("sounds/hihat.wav"),

    # Middle row
    "HIHAT_OPEN":   pygame.mixer.Sound("sounds/hihat.wav"),
    "TOM1":         pygame.mixer.Sound("sounds/tom.wav"),
    "TOM2":         pygame.mixer.Sound("sounds/tom.wav"),
    "FLOOR_TOM":    pygame.mixer.Sound("sounds/tom.wav"),

    # Bottom row
    "BASS":         pygame.mixer.Sound("sounds/bass.wav"),
}

DRUMS = {
    # (x1, y1, x2, y2)
    "HIHAT_CLOSED": (40, 40, 240, 180),
    "SNARE":        (260, 40, 460, 180),
    "CRASH":        (780, 40, 980, 180),
    "RIDE":         (1000, 40, 1200, 180),

    "HIHAT_OPEN":   (40, 200, 240, 360),
    "TOM1":         (500, 200, 700, 360),
    "TOM2":         (720, 200, 920, 360),
    "FLOOR_TOM":    (940, 200, 1140, 360),

    "BASS":         (500, 450, 840, 650),
}

HIT_COOLDOWN = 0.25
# Cooldown per drum zone so each pad can be hit independently
last_hit_time = {drum: 0 for drum in DRUMS}
active_drums = {}  # drum_name -> hit timestamp for visual flash

def draw_drums(frame):
    import cv2
    current_time = time.time()
    for drum, (x1, y1, x2, y2) in DRUMS.items():
        # Flash yellow briefly when a pad is hit, otherwise stay green
        if drum in active_drums and current_time - active_drums[drum] < 0.12:
            color = (0, 220, 255)
            thickness = 3
        else:
            color = (0, 255, 0)
            thickness = 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(frame, drum, (x1 + 10, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def process_hit(hand_name, index_tip, wrist):
    """index_tip (x,y) triggers all drums except BASS; wrist (x,y) triggers BASS."""
    current_time = time.time()

    for drum_name, (x1, y1, x2, y2) in DRUMS.items():
        cx, cy = wrist if drum_name == "BASS" else index_tip
        if x1 < cx < x2 and y1 < cy < y2:
            if current_time - last_hit_time[drum_name] > HIT_COOLDOWN:
                if drum_name in SOUNDS:
                    SOUNDS[drum_name].play()
                last_hit_time[drum_name] = current_time
                active_drums[drum_name] = current_time
