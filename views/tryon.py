import streamlit as st
import cv2
import os
from src.tryon import overlay_glasses, run_live_tryon


def show():
    st.title("🕶️ Virtual Try-On")

    if "last_result" not in st.session_state:
        st.warning("Please analyze a photo on the Home page first.")
        return

    result = st.session_state["last_result"]
    image = st.session_state["last_image"]

    if result.get("face_landmarks") is None:
        st.error("No face landmarks available for this photo. Please re-analyze a photo on the Home page.")
        return

    st.write(f"Detected shape: **{result['recommendation']['primary_shape']}**")

    recommended_frames = result["recommendation"]["recommended"]

    # Build a lookup: display name -> real image path, only if the file actually exists
    frame_options = {}
    for item in recommended_frames:
        image_path = f"assets/glasses/{item['image_filename']}"
        if os.path.exists(image_path):
            frame_options[item["frame_name"]] = image_path

    if not frame_options:
        st.info("No try-on images available for your recommended frames yet.")
        return

    chosen_frame = st.selectbox("Choose a specific frame to try on", list(frame_options.keys()))
    glasses_path = frame_options[chosen_frame]

    if st.button("Show Try-On"):
        if not os.path.exists(glasses_path):
            st.error("This frame's image is currently unavailable. Please choose a different style.")
            st.stop()

        tryon_image = image.copy()
        tryon_result = overlay_glasses(
            tryon_image,
            result["face_landmarks"],
            glasses_path,
            image.shape[1],
            image.shape[0]
        )

        st.image(
            cv2.cvtColor(tryon_result, cv2.COLOR_BGR2RGB),
            caption=f"{chosen_frame} Try-On",
            width=400
        )

    if st.button("🎥 Try This Live on Camera"):
        st.info("Opening camera window... press Q in that window to close it.")
        run_live_tryon(glasses_path)