import cv2
import mediapipe as mp

from src.measurements import calculate_measurements
from src.face_shape import classify_face_shape
from src.recommender import recommend_glasses

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


def analyze_image(image):
    """
    Analyze one image and return results.
    """

    h, w, _ = image.shape

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:

        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {
                "success": False,
                "image": image,
                "measurements": None,
                "face_shape": None,
                "recommendation": None,
                "message": "No face detected.",
            }

        
        multiple_faces_detected = len(results.multi_face_landmarks) > 1
        face_landmarks = results.multi_face_landmarks[0]  # still only use the first one

        # Draw mesh
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing.DrawingSpec(
                thickness=1,
                circle_radius=1,
            ),
        )

        # Measurements
        measurements = calculate_measurements(
            face_landmarks,
            w,
            h,
        )

        # Face shape
        face_shape, confidence, shape_probabilities = classify_face_shape(measurements)


        # Recommendation
        #recommendation = recommend_glasses(face_shape)
        recommendation = recommend_glasses(shape_probabilities)

        return {

        "success": True,
        "image": image,
        "measurements": measurements,
        "face_shape": face_shape,
        "confidence": confidence,
        "shape_probabilities": shape_probabilities,
        "recommendation": recommendation,
        "face_landmarks": face_landmarks,
        "message": "Success",
}

# image = cv2.imread("E:/LensMatch-AI/FaceShape_Dataset/testing_set/Heart")
# result = analyze_image(image)
# print(result["face_shape"], result["confidence"])
# print(result["shape_probabilities"])