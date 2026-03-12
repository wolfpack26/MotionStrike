import cv2
import platform

def open_camera():
    system = platform.system()

    if system == "Darwin":        # macOS
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)

    elif system == "Windows":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    else:                         # Linux
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not open camera")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Safe default resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    return cap