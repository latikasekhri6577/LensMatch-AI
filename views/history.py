import streamlit as st
from src.auth import get_scan_history


def show():
    st.title("📜 Your Scan History")

    username = st.session_state["username"]
    history = get_scan_history(username)

    if not history:
        st.info("No scans yet. Go analyze a photo on the Home page first.")
        return

    for row in history:
        face_shape, confidence, face_width, face_height, aspect_ratio, frames, scanned_at = row

        with st.container(border=True):
            st.write(f"**{face_shape}** — {confidence:.0%} confidence")
            st.caption(f"Scanned on {scanned_at[:19].replace('T', ' ')}")
            st.write(f"Recommended: {frames}")
            with st.expander("Measurements"):
                st.write(f"Face width: {face_width:.1f}px")
                st.write(f"Face height: {face_height:.1f}px")
                st.write(f"Aspect ratio: {aspect_ratio:.2f}")