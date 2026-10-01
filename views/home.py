import streamlit as st
import cv2
import numpy as np
import pandas as pd
from src.face_mesh import analyze_image
from src.camera import run_camera
from src.report import generate_report
from src.auth import save_scan
from src.favourites import add_favorite, remove_favorite, is_favorited
from src.measurements import is_blurry
from src.groq_client import get_model_name


def show():
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <h1 style="font-size: 48px; margin-bottom: 0;">👓 LensMatch-AI</h1>
            <p style="font-size: 18px; color: #9aa0a6; margin-top: 5px;">
                AI Smart Eyeglasses Recommender
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    col1, col2 = st.columns(2)

    # ==========================
    # LEFT COLUMN
    # ==========================
    with col1:
        with st.container(border=True):
            st.header("📤 Upload Face Image")

            uploaded_file = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png"]
            )

        if uploaded_file is not None:

            file_bytes = np.asarray(
                bytearray(uploaded_file.read()),
                dtype=np.uint8
            )

            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image is None:
                st.error("This file couldn't be read as an image. Please upload a valid JPG or PNG.")
                st.stop()

            # Reject suspiciously tiny images (likely corrupted or not a real photo)
            h, w = image.shape[:2]
            if h < 50 or w < 50:
                st.error("This image is too small to analyze. Please upload a clearer photo.")
                st.stop()

            # Blur check - just a warning, doesn't block the rest of the flow
            if is_blurry(image):
                st.warning("This photo looks a bit blurry — results may be less accurate. Consider uploading a sharper image.")

            st.image(
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                caption="Uploaded Image",
                width=400
            )

            if st.button("Analyze Face"):
                original_image_copy = image.copy()
                with st.spinner("Analyzing..."):
                    try:
                        result = analyze_image(image)
                    except Exception:
                        st.error("Something went wrong while analyzing this photo. Please try a different image.")
                        st.stop()

                if result["success"]:
                    st.session_state["last_result"] = result
                    st.session_state["last_image"] = original_image_copy

                    rec = result["recommendation"]
                    save_scan(
                        username=st.session_state["username"],
                        face_shape=rec["primary_shape"],
                        confidence=result["confidence"],
                        measurements=result["measurements"],
                        recommended_frames=[item["frame_name"] for item in rec["recommended"]]
                    )

                    if result.get("multiple_faces_detected"):
                        st.warning("Multiple faces detected — analysis was performed on one face only. For best results, use a photo with a single face.")

                else:
                    st.error(result["message"])

            # --- Everything below reads from session_state, not the button click ---
            if "last_result" in st.session_state:
                result = st.session_state["last_result"]
                rec = result["recommendation"]

                st.success("Face detected!")

                st.image(
                    cv2.cvtColor(result["image"], cv2.COLOR_BGR2RGB),
                    caption="Face Mesh",
                    width=400
                )

                st.subheader("Face Shape")
                st.write(result["face_shape"])

                st.subheader("Measurements")

      

                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric("Face Width", f"{result['measurements']['face_width']:.0f} px")
                with metric_col2:
                    st.metric("Face Height", f"{result['measurements']['face_height']:.0f} px")
                with metric_col3:
                    st.metric("Aspect Ratio", f"{result['measurements']['aspect_ratio']:.2f}")

                st.subheader("Face Shape Result")
                if rec["is_blended"]:
                    st.info(
                        f"Your face shows a mix of **{rec['primary_shape']}** and "
                        f"**{rec['secondary_shape']}** traits ({result['confidence']:.0%} "
                        f"confidence on top guess) — showing recommendations that suit both."
                    )
                else:
                    st.write(
                        f"Detected shape: **{rec['primary_shape']}** "
                        f"({result['confidence']:.0%} confidence)"
                    )

                st.subheader("Confidence Breakdown")
                import pandas as pd
                prob_df = pd.DataFrame(
                    list(result["shape_probabilities"].items()),
                    columns=["Shape", "Probability"]
                ).set_index("Shape")
                st.bar_chart(prob_df)

                st.subheader("Ask the AI")
                if st.button("Ask AI why these frames?"):
                    from src.groq_client import get_client
                    client = get_client()

                    explanation_prompt = (
                        f"A user's face was analyzed as {rec['primary_shape']} "
                        f"(confidence {result['confidence']:.0%}). "
                        f"Their measurements: face width {result['measurements']['face_width']:.0f}px, "
                        f"face height {result['measurements']['face_height']:.0f}px, "
                        f"aspect ratio {result['measurements']['aspect_ratio']:.2f}. "
                        f"Recommended frames: {', '.join(item['frame_name'] for item in rec['recommended'])}. "
                        f"Explain in 3-4 friendly sentences why these frames suit this face shape."
                    )
                    with st.spinner("Thinking..."):
                        try:
                            response = client.chat.completions.create(
                                model=get_model_name(),
                                messages=[
                                    {"role": "system", "content": "You are a helpful eyewear styling expert."},
                                    {"role": "user", "content": explanation_prompt}
                                ]
                            )
                            explanation = response.choices[0].message.content
                        except Exception as e:
                            st.error("The AI assistant is temporarily unavailable. Please try again in a moment.")
                            st.stop()

                    st.write(explanation)

                    if "chat_messages" not in st.session_state:
                        st.session_state["chat_messages"] = [
                            {"role": "system", "content": "You are a friendly eyewear styling assistant for LensMatch-AI."}
                        ]
                    st.session_state["chat_messages"].append({"role": "user", "content": explanation_prompt})
                    st.session_state["chat_messages"].append({"role": "assistant", "content": explanation})

                st.subheader("Recommended Frames")
                for frame in rec["recommended"]:
                    frame_col1, frame_col2 = st.columns([4, 1])
                    with frame_col1:
                        st.write("✅", frame["frame_name"])
                    with frame_col2:
                        already_saved = is_favorited(st.session_state["username"], frame["frame_name"])
                        heart_label = "💔 Remove" if already_saved else "❤️ Save"
                        if st.button(heart_label, key=f"fav_{frame['frame_name']}"):
                            if already_saved:
                                remove_favorite(st.session_state["username"], frame["frame_name"])
                            else:
                                add_favorite(st.session_state["username"], frame["frame_name"], rec["primary_shape"])
                            st.rerun()

                st.subheader("Frames to Avoid")
                for frame in rec["avoid"]:
                    st.write("❌", frame)

                st.header("Download Report")
                pdf_path = generate_report(
                    result["measurements"],
                    result["face_shape"],
                    result["recommendation"]
                )
                with open(pdf_path, "rb") as pdf:
                    st.download_button(
                        "Download Report",
                        pdf,
                        file_name="LensMatch_Report.pdf",
                        mime="application/pdf"
                    )

    # ==========================
    # RIGHT COLUMN
    # ==========================
    with col2:
        with st.container(border=True):
            st.header("🎥 Live Camera")

            if st.button("Start Camera"):
                run_camera()

            st.markdown("---")