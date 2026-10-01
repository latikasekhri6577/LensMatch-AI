import cv2
import mediapipe as mp
from src.measurements import calculate_measurements

mp_face_mesh = mp.solutions.face_mesh

def extract_features(image):
    """
    Pure feature extraction for training. No drawing, no classification.
    Returns dict of measurements, or None if no face detected.
    """
    h, w, _ = image.shape
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:

        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        face_landmarks = results.multi_face_landmarks[0]
        return calculate_measurements(face_landmarks, w, h)



        