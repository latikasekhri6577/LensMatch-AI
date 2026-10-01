import streamlit as st
from src.auth import init_db, create_user, verify_user
from src.favourites import init_favorites_table

init_db()  #ensures the table exists every time the app starts

init_favorites_table()  

def show():
    st.title("👓 LensMatch-AI")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    # ---------------- LOGIN ----------------
    with tab_login:
        st.subheader("Login to your account")

        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if verify_user(login_username, login_password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = login_username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    # ---------------- SIGN UP ----------------
    with tab_signup:
        st.subheader("Create a new account")

        new_username = st.text_input("Choose a username", key="signup_username")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Choose a password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = create_user(new_username, new_email, new_password)
                if success:
                    st.success(message + " Please log in now.")
                else:
                    st.error(message)