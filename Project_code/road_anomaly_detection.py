from enhancement import enhance_single_image
import cv2
import numpy as np
import time

# ==========================
# CONFIGURATION
# ==========================
FRAME_W, FRAME_H = 320, 240

VAR_POTHOLE = 180
VAR_CRACK = 120
VAR_SPEED = 120

MIN_AREA = 300
SPEED_AREA = 8000

TURN_ANGLE_VAR = 0.8
TURN_FLOW = 1.2

TEMPORAL_FRAMES = 3
TTC_THRESHOLD = 0.7
MIN_FLOW_MAG = 40.0

# ==========================
# OPEN STREAM
# ==========================
def open_stream():
    pipeline = (
        "libcamerasrc ! "
        "video/x-raw,format=RGB,width=320,height=240,framerate=30/1 ! "
        "videoconvert ! "
        "appsink drop=true"
    )

    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("❌ Cannot open PiCam")
        return None

    print("✅ PiCam connected")
    return cap


cap = open_stream()
if cap is None:
    exit()

# ==========================
# VARIABLES
# ==========================
prev_gray = None
counter = 0
final_label = "NORMAL"

night_mode = False
clahe = cv2.createCLAHE(2.0, (8, 8))

fps_counter = 0
fps_timer = time.time()
fps = 0

# ==========================
# MAIN LOOP
# ==========================
while True:

    for _ in range(5):
        cap.grab()

    ret, frame = cap.read()

    if not ret:
        print("⚠ Stream stalled → reconnecting...")
        cap.release()
        time.sleep(0.5)
        cap = open_stream()
        prev_gray = None
        continue

    # Night mode enhancement
    if night_mode:
        frame = enhance_single_image(frame)

    collision_risk = False

    # Night sensitivity adjustment
    if night_mode:
        min_flow_mag = 15.0
        ttc_threshold = 1.2
        min_area = 150
    else:
        min_flow_mag = 40.0
        ttc_threshold = 0.7
        min_area = 300

    h, w = frame.shape[:2]
    roi = frame[int(h * 0.4):h, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    norm = clahe.apply(gray)

    blur = cv2.GaussianBlur(norm, (5, 5), 0)
    mean = cv2.blur(blur, (15, 15))
    variance_map = cv2.blur((blur - mean) ** 2, (15, 15))
    variance = np.mean(variance_map)

    edges = cv2.Canny(norm, 50, 120)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    label = "NORMAL"

    if contours:
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)

        if area > min_area:

            x, y, bw, bh = cv2.boundingRect(c)
            aspect_ratio = bw / float(bh)

            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull) + 1e-5
            solidity = area / hull_area

            gx = cv2.Sobel(norm, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(norm, cv2.CV_64F, 0, 1, ksize=3)
            angles = np.arctan2(gy, gx)
            angle_variance = np.var(angles)

            mean_flow = 0
            ttc = np.inf

            if prev_gray is not None:

                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, norm,
                    None,
                    0.5, 2, 9, 2, 5, 1.1, 0
                )

                fx = flow[..., 0]
                fy = flow[..., 1]

                mag = np.sqrt(fx**2 + fy**2)
                mean_flow = np.mean(np.abs(fx))

                Y, X = np.mgrid[0:mag.shape[0], 0:mag.shape[1]]
                cx, cy = mag.shape[1] / 2, mag.shape[0] / 2

                dx = X - cx
                dy = Y - cy

                dist = np.sqrt(dx**2 + dy**2) + 1e-4
                radial_flow = (fx * dx + fy * dy) / dist

                valid = mag > min_flow_mag
                expansion = radial_flow[valid]

                if expansion.size > 0:
                    mean_expansion = np.mean(expansion)
                    if mean_expansion > 0:
                        ttc = 1.0 / mean_expansion

                if ttc < ttc_threshold:
                    collision_risk = True
                    cv2.putText(frame, "COLLISION RISK!",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 0, 255), 2)

            if angle_variance > TURN_ANGLE_VAR and mean_flow > TURN_FLOW:
                label = "TURN"

            elif variance > VAR_POTHOLE and solidity < 0.9:
                label = "POTHOLE"

            elif aspect_ratio > 3.0 and variance > VAR_CRACK:
                label = "CRACK / ROUGH"

            elif area > SPEED_AREA and variance < VAR_SPEED:
                label = "SPEED BREAKER"

    if label != "NORMAL":
        counter += 1
    else:
        counter = 0
        final_label = "NORMAL"

    if counter >= TEMPORAL_FRAMES and not collision_risk:
        final_label = label

    prev_gray = norm.copy()

    fps_counter += 1
    if time.time() - fps_timer >= 1:
        fps = fps_counter
        fps_counter = 0
        fps_timer = time.time()

    cv2.putText(frame, final_label, (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.putText(frame, f"FPS: {fps}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    mode_text = "NIGHT MODE ON" if night_mode else "NIGHT MODE OFF"
    cv2.putText(frame, mode_text, (10, 105),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 255, 255), 2)

    cv2.imshow("Road Monitoring System", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('n'):
        night_mode = not night_mode

cap.release()
cv2.destroyAllWindows()
print("\n========== SYSTEM SHUTDOWN ==========")
