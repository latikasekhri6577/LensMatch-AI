## Phase 1: ML-Based Face Shape Classification

### Overview
Replaced the original rule-based (if/elif threshold) face shape classifier 
with a trained machine learning model, converting the project from a 
computer vision script into a full ML pipeline.

### Dataset
- **Source:** [Face Shape Dataset](https://www.kaggle.com/datasets/niten19/face-shape-dataset) (Kaggle, by Niten Lama)
- **Classes:** Heart, Oblong, Oval, Round, Square (5 classes)
- **Size:** 5,000 images total — 4,000 training / 1,000 testing (800/200 per class)

### Pipeline
1. **Feature extraction:** Used MediaPipe Face Mesh to extract facial landmarks 
   from each image, then computed geometric ratio features (scale-invariant, 
   so they work regardless of image resolution):
   - `aspect_ratio` — face height/width
   - `forehead_ratio`, `cheek_ratio`, `jaw_ratio` — width ratios relative to face width
   - `chin_to_jaw_ratio` — chin width relative to jaw width (captures chin pointedness)
   - `jaw_angle` — angle formed at the chin between jaw corners (captures jawline shape)
   - `jowl_taper_ratio` — how quickly the face narrows from cheekbone to jaw
2. **Model:** GradientBoostingClassifier