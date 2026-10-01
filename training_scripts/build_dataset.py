import os
import cv2
import pandas as pd
from src.features import extract_features

FEATURE_COLS = [
    "aspect_ratio", "forehead_ratio", "cheek_ratio", "jaw_ratio",
    "chin_to_jaw_ratio", "jaw_angle", "jowl_taper_ratio"
]

def build_csv(data_dir, output_csv):
    rows = []
    skipped = 0

    for label in os.listdir(data_dir):
        class_dir = os.path.join(data_dir, label)
        if not os.path.isdir(class_dir):
            continue

        files = os.listdir(class_dir)
        print(f"Processing {label}: {len(files)} images")

        for fname in files:
            path = os.path.join(class_dir, fname)
            image = cv2.imread(path)
            if image is None:
                skipped += 1
                continue

            measurements = extract_features(image)
            if measurements is None:
                skipped += 1
                continue

            row = {col: measurements[col] for col in FEATURE_COLS}
            row["label"] = label
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} rows to {output_csv} ({skipped} skipped)")
    print(df["label"].value_counts())
    return df

if __name__ == "__main__":
    build_csv("FaceShape_Dataset/training_set", "features_train.csv")
    build_csv("FaceShape_Dataset/testing_set", "features_test.csv")