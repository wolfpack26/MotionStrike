import pygame
import time
import math

pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()

SOUNDS = {
    # Top row
    "HIHAT_CLOSED": pygame.mixer.Sound("sounds/closed_hihat.wav"),
    "SNARE":        pygame.mixer.Sound("sounds/snare.wav"),
    "CRASH":        pygame.mixer.Sound("sounds/crash_cymbal.wav"),
    "RIDE":         pygame.mixer.Sound("sounds/hihat.wav"),

    # Middle row
    "HIHAT_OPEN":   pygame.mixer.Sound("sounds/open_hihat.wav"),
    "HIGH TOM":     pygame.mixer.Sound("sounds/high_tom.wav"),
    "MID TOM":      pygame.mixer.Sound("sounds/mid_tom.wav"),
    "FLOOR_TOM":    pygame.mixer.Sound("sounds/floor_tom.wav"),

    # Bottom row
    "BASS":         pygame.mixer.Sound("sounds/bass.wav"),
}

DRUMS = {
    # (x1, y1, x2, y2)
    "HIHAT_CLOSED": (40, 40, 240, 330),
    "SNARE":        (260, 40, 460, 330),
    "CRASH":        (680, 40, 880, 180),
    "RIDE":         (980, 40, 1180, 180),

    "HIHAT_OPEN":   (40, 360, 240, 700),
    "HIGH TOM":     (700, 200, 920, 420),
    "MID TOM":      (940, 200, 1160, 420),
    "FLOOR_TOM":    (960, 440, 1160, 700),

    "BASS":         (500, 450, 840, 650),
}

HIT_COOLDOWN = 0.15

last_hit_time = {drum: 0 for drum in DRUMS}
active_drums = {}
pygame.mixer.set_num_channels(len(DRUMS) + 4)
_CHANNELS = {drum: pygame.mixer.Channel(i) for i, drum in enumerate(DRUMS)}

# --- Velocity / intent thresholds (px/s) — tune to taste ---
MIN_HIT_VELOCITY = 200
MAX_HIT_VELOCITY = 1500
MIN_DOWNWARD_DY  = 2

# --- Z-depth gate (MediaPipe z: negative = pushed toward camera) ---
Z_STRIKE_THRESHOLD = 0.1
DEBUG_Z = False

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

def process_hit(hand_name, index_tip, thumb,
                velocity=float('inf'), dy=float('inf'), index_z=0.0):
    """
    index_tip (x,y) -- triggers all drums except BASS
    thumb     (x,y) -- triggers BASS
    velocity        -- px/s of tracked point (intent gate + volume)
    dy              -- vertical displacement since last sample (+ve = downward)
    index_z         -- MediaPipe z of landmark 8 (negative = toward camera)
    Defaults to float('inf') so sticks.py calls bypass all gates at full volume.
    """
    current_time = time.time()

    # Map velocity to a 0.1–1.0 volume
    raw_vol = (velocity - MIN_HIT_VELOCITY) / (MAX_HIT_VELOCITY - MIN_HIT_VELOCITY)
    volume  = max(0.1, min(1.0, raw_vol))

    for drum_name, (x1, y1, x2, y2) in DRUMS.items():
        cx, cy = thumb if drum_name == "BASS" else index_tip
        if x1 < cx < x2 and y1 < cy < y2:
            if current_time - last_hit_time[drum_name] > HIT_COOLDOWN:
                # Intent gate: must be a downward strike above minimum speed
                if velocity < MIN_HIT_VELOCITY or dy < MIN_DOWNWARD_DY:
                    continue
                # Z-depth gate: skip for BASS (thumb z is always 0)
                if drum_name != "BASS" and index_z > Z_STRIKE_THRESHOLD:
                    continue
                if drum_name in SOUNDS:
                    ch = _CHANNELS[drum_name]
                    ch.set_volume(volume)
                    ch.play(SOUNDS[drum_name])
                last_hit_time[drum_name] = current_time
                active_drums[drum_name] = current_time
