import cv2
import numpy as np
import mediapipe as mp
import streamlit as st

mp_face_mesh = mp.solutions.face_mesh


def run_live_tryon(glasses_path):
    """
    Opens the webcam and overlays the given glasses image on the live feed.
    Separate from src/camera.py - used only by the Virtual Try-On page.
    """

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Could not access the camera. Please check that it's connected and not in use by another application.")
        return

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while True:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                frame = overlay_glasses(frame, face_landmarks, glasses_path, w, h)

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            cv2.imshow("LensMatch AI - Live Try-On", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


def overlay_glasses(image, face_landmarks, glasses_path, w, h):
    """
    Puts a transparent glasses PNG onto the face image,
    positioned using eye landmarks.
    """

    lm = face_landmarks.landmark

    left_eye = lm[33]
    right_eye = lm[263]

    left_x, left_y = int(left_eye.x * w), int(left_eye.y * h)
    right_x, right_y = int(right_eye.x * w), int(right_eye.y * h)

    eye_distance = np.sqrt((right_x - left_x) ** 2 + (right_y - left_y) ** 2)

    glasses = cv2.imread(glasses_path, cv2.IMREAD_UNCHANGED)
    if glasses is None:
        raise FileNotFoundError(f"Glasses asset not found: {glasses_path}")

    gh, gw = glasses.shape[:2]

    new_width = int(eye_distance * 2.2)
    scale = new_width / gw
    new_height = int(gh * scale)

    glasses_resized = cv2.resize(glasses, (new_width, new_height))

    center_x = (left_x + right_x) // 2
    center_y = (left_y + right_y) // 2

    x_offset = center_x - new_width // 2
    y_offset = center_y - new_height // 2

    return _blend_transparent(image, glasses_resized, x_offset, y_offset)


def _blend_transparent(background, overlay, x_offset, y_offset):
    """Pastes the overlay onto the background, respecting transparency."""

    bh, bw = background.shape[:2]
    oh, ow = overlay.shape[:2]

    x1, y1 = max(x_offset, 0), max(y_offset, 0)
    x2, y2 = min(x_offset + ow, bw), min(y_offset + oh, bh)

    if x1 >= x2 or y1 >= y2:
        return background

    overlay_crop = overlay[
        y1 - y_offset: y2 - y_offset,
        x1 - x_offset: x2 - x_offset
    ]

    alpha = overlay_crop[:, :, 3] / 255.0
    alpha = alpha[:, :, np.newaxis]

    background_region = background[y1:y2, x1:x2]
    blended = (alpha * overlay_crop[:, :, :3] + (1 - alpha) * background_region).astype(np.uint8)

    background[y1:y2, x1:x2] = blended
    return background