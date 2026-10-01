import streamlit as st
from src.favourites import get_favorites, remove_favorite


def show():
    st.title("❤️ Your Saved Frames")

    username = st.session_state["username"]
    favorites = get_favorites(username)

    if not favorites:
        st.info("No saved frames yet. Heart a recommendation on the Home page to save it here.")
        return

    for frame_name, frame_style, added_at in favorites:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{frame_name}**")
                st.caption(f"Matched to: {frame_style} | Saved {added_at[:19].replace('T', ' ')}")
            with col2:
                if st.button("Remove", key=f"remove_{frame_name}"):
                    remove_favorite(username, frame_name)
                    st.rerun()