import joblib
import os
import pandas as pd

MODEL_PATH = os.path.join("models", "face_shape_model.pkl")
ENCODER_PATH = os.path.join("models", "label_encoder.pkl")

# Load once at import time, not per-request
_model = joblib.load(MODEL_PATH)
_label_encoder = joblib.load(ENCODER_PATH)

FEATURE_COLS = [
    "aspect_ratio", "forehead_ratio", "cheek_ratio", "jaw_ratio",
    "chin_to_jaw_ratio", "jaw_angle", "jowl_taper_ratio"
]


def classify_face_shape(measurements):
    """
    Predicts face shape using the trained model.
    Returns (shape_label, confidence, full_probabilities_dict)
    """

    # Build feature vector in the exact order the model was trained on
    #X = [[measurements[col] for col in FEATURE_COLS]]
    X = pd.DataFrame([[measurements[col] for col in FEATURE_COLS]], columns=FEATURE_COLS)

    # Get predicted class and full probability distribution
    pred_encoded = _model.predict(X)[0]
    probabilities = _model.predict_proba(X)[0]

    shape = _label_encoder.inverse_transform([pred_encoded])[0]
    confidence = max(probabilities)

    # Build a readable dict: {"Oval": 0.45, "Heart": 0.38, ...}
    prob_dict = {
        label: round(float(prob), 4)
        for label, prob in zip(_label_encoder.classes_, probabilities)
    }

    return shape, confidence, prob_dict