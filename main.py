import streamlit as st
import hashlib
import base64
from PIL import Image
from io import BytesIO
import time
import database as db


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def navigate_to_signup():
    st.session_state.page = "signup"


def navigate_to_login():
    st.session_state.page = "login"

if "login" not in st.session_state:
    st.session_state.login = True


if st.session_state.login:
    # Image
    image_path = 'logo.png'
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    html_code = f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{img_base64}" width="50" style="display: block; margin: 0 auto;" />
        </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        st.title("Welcome Back!")

        # Login section
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_button = st.button("Login")

        if login_button:
            if db.login(username, hash_password(password)):
                st.success(f"Welcome {username}")
                time.sleep(2)
                st.session_state.log_in_user = username
                st.session_state.login = False
                st.switch_page("pages/home.py")


            else:
                st.error("Invalid username or password")

        # Navigate to sign-up page
        st.button("Sign Up", on_click=navigate_to_signup)

    elif st.session_state.page == "signup":
        st.title("Getting Started")

        # Sign Up section
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        signup_button = st.button("Sign Up Now")

        if signup_button:
            if db.add_user(new_user, hash_password(new_password)):
                st.success("You have successfully created an account!")

            else:
                st.error("Username already exists")

        # Navigate back to login page
        st.button("Back to Login", on_click=navigate_to_login)
