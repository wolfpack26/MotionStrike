import pygame
import time

pygame.mixer.init()

SOUNDS = {
    "SNARE": pygame.mixer.Sound("sounds/snare.wav"),
    "HIHAT": pygame.mixer.Sound("sounds/hihat.wav"),
    "BASS":  pygame.mixer.Sound("sounds/bass.wav"),
}

DRUMS = { 
    "SNARE": (50, 50, 350, 250),
    "HIHAT": (400, 50, 700, 250),
    "BASS": (750, 50, 1050, 250),
}

HIT_COOLDOWN = 0.25
last_hit_time = {"Left": 0, "Right": 0}

def draw_drums(frame):
    import cv2
    for drum, (x1, y1, x2, y2) in DRUMS.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, drum, (x1 + 10, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

def process_hit(hand_name, cx, cy):
    current_time = time.time()

    for drum_name, (x1, y1, x2, y2) in DRUMS.items():
        if x1 < cx < x2 and y1 < cy < y2:
            if current_time - last_hit_time[hand_name] > HIT_COOLDOWN:
                SOUNDS[drum_name].play()
                last_hit_time[hand_name] = current_time
