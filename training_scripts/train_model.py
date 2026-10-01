import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

FEATURE_COLS = [
    "aspect_ratio", "forehead_ratio", "cheek_ratio", "jaw_ratio",
    "chin_to_jaw_ratio", "jaw_angle", "jowl_taper_ratio"
]

train_df = pd.read_csv("features_train.csv")
test_df = pd.read_csv("features_test.csv")

X_train, y_train = train_df[FEATURE_COLS], train_df["label"]
X_test, y_test = test_df[FEATURE_COLS], test_df["label"]

le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=3,
    random_state=42
)
model.fit(X_train, y_train_enc)

preds = model.predict(X_test)

print("=== Classification Report ===")
print(classification_report(y_test_enc, preds, target_names=le.classes_))

print("=== Confusion Matrix ===")
print("Classes order:", list(le.classes_))
print(confusion_matrix(y_test_enc, preds))

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/face_shape_model.pkl")
joblib.dump(le, "models/label_encoder.pkl")
print("\nSaved model to models/face_shape_model.pkl")