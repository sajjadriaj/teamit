import streamlit as st
import yaml
import streamlit_authenticator as stauth
from db.ops import fetch_users, insert_user, get_usernames, get_user_emails
from auth import sign_up

st.set_page_config(page_title="Hello", page_icon="👋", layout="wide")

users = fetch_users()
emails = []
usernames = []
passwords = []

for user in users:
    emails.append(user["key"])
    usernames.append(user["username"])
    passwords.append(user["password"])

credentials = {"usernames": {}}
for index in range(len(emails)):
    credentials["usernames"][usernames[index]] = {
        "name": emails[index],
        "password": passwords[index],
    }

Authenticator = stauth.Authenticate(
    credentials, cookie_name="Streamlit", cookie_key="abc", cookie_expiry_days=4
)

if "authention_status" in st.session_state and st.session_state["authention_status"]:
    st.write("You are authenticated")
else:
    """
    Welcome to Teamit! Please sign in to continue or sign up if you don't have an account.
    """
    # Initialize the session state for form control
    if "current_form" not in st.session_state:
        st.session_state["current_form"] = "login"

    # Buttons for toggling between forms
    if st.button("Go to Sign Up"):
        st.session_state["current_form"] = "signup"
    if st.button("Go to Login"):
        st.session_state["current_form"] = "login"

    # Display the appropriate form based on the current state
    if st.session_state["current_form"] == "login":
        Authenticator.login()
    elif st.session_state["current_form"] == "signup":
        sign_up()
