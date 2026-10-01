CONFIDENCE_THRESHOLD = 0.55
import os
import pandas as pd

CSV_PATH = os.path.join("data", "glasses.csv")
_glasses_df = pd.read_csv(CSV_PATH)

def _shape_in_list(shape, cell_value):
    if pd.isna(cell_value):
        return False
    shapes = [s.strip() for s in cell_value.split(",")]
    return shape in shapes


def _get_recommendations_for_shape(shape, top_n):
    df = _glasses_df

    suitable_mask = df["suitable_shapes"].apply(lambda cell: _shape_in_list(shape, cell))
    avoid_mask = df["avoid_shapes"].apply(lambda cell: _shape_in_list(shape, cell))

    matched = df[suitable_mask].head(top_n)
    recommended = matched[["frame_name", "image_filename"]].to_dict("records")
    avoid = df[avoid_mask]["frame_name"].tolist()

    return recommended, avoid


def recommend_glasses(shape_probabilities, top_n=5):
    """
    Confidence-aware recommendation.
    shape_probabilities: dict like {"Oval": 0.45, "Square": 0.30, ...}
    """

    sorted_shapes = sorted(
        shape_probabilities.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_shape, top_confidence = sorted_shapes[0]

    if top_confidence >= CONFIDENCE_THRESHOLD:
        recommended, avoid = _get_recommendations_for_shape(top_shape, top_n)
        return {
            "primary_shape": top_shape,
            "secondary_shape": None,
            "is_blended": False,
            "recommended": recommended,
            "avoid": avoid
        }

    second_shape, second_confidence = sorted_shapes[1]

    rec_1, avoid_1 = _get_recommendations_for_shape(top_shape, top_n)
    rec_2, avoid_2 = _get_recommendations_for_shape(second_shape, top_n)

    seen = set()
    merged_recommended_raw = []
    for item in rec_1 + rec_2:
        if item["frame_name"] not in seen:
            seen.add(item["frame_name"])
            merged_recommended_raw.append(item)

    merged_avoid = list(dict.fromkeys(avoid_1 + avoid_2))

    merged_recommended = [
        item for item in merged_recommended_raw
        if item["frame_name"] not in merged_avoid
    ][:top_n]

    return {
        "primary_shape": top_shape,
        "secondary_shape": second_shape,
        "is_blended": True,
        "recommended": merged_recommended,
        "avoid": merged_avoid
    }