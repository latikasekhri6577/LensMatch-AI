import streamlit as st
from views import home, tryon, auth_page, chat_assistant, history,favourites

st.set_page_config(page_title="LensMatch-AI", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    auth_page.show()
else:
    pages = {
        "LensMatch-AI": [
            st.Page(home.show, title="Home", icon="👓", url_path="home"),
            st.Page(tryon.show, title="Virtual Try-On", icon="🕶️", url_path="tryon"),
            st.Page(chat_assistant.show, title="Style Assistant", icon="💬", url_path="chat"),
            st.Page(history.show, title="History", icon="📜", url_path="history"),
            st.Page(favourites.show, title="Favorites", icon="❤️", url_path="favorites")
        ]
    }
    pg = st.navigation(pages, position="top")
    pg.run()

    with st.sidebar:
        st.write(f"Logged in as **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()


    