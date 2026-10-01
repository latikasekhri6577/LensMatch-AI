import cv2
import mediapipe as mp
import streamlit as st

from src.measurements import calculate_measurements
from src.face_shape import classify_face_shape
from src.recommender import recommend_glasses

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


def run_camera():

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

                for face_landmarks in results.multi_face_landmarks:

                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing.DrawingSpec(
                            thickness=1,
                            circle_radius=1,
                        ),
                    )

                    measurements = calculate_measurements(
                        face_landmarks,
                        w,
                        h,
                    )

                    face_shape, confidence, shape_probabilities = classify_face_shape(measurements)

                    recommendation = recommend_glasses(shape_probabilities)

                    cv2.putText(
                        frame,
                        f"Face Shape: {face_shape}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"Width: {int(measurements['face_width'])}",
                        (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"Height: {int(measurements['face_height'])}",
                        (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"Aspect Ratio: {measurements['aspect_ratio']:.2f}",
                        (20, 160),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        "Best Frames:",
                        (20, 220),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

                    y = 260

                    for frame_item in recommendation["recommended"]:
                        cv2.putText(
                            frame,
                            f"- {frame_item['frame_name']}",
                            (40, y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )
                        y += 35

            cv2.imshow("LensMatch AI", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()