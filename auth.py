import re
import streamlit as st
from db.ops import fetch_users, get_user_emails, get_usernames, insert_user
import streamlit_authenticator as stauth


def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"  # tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False


def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """

    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False


def sign_up():
    with st.form(key="signup", clear_on_submit=True):
        st.subheader("Sign Up")
        email = st.text_input("Email", placeholder="Enter Your Email")
        username = st.text_input("Username", placeholder="Enter Your Username")
        password1 = st.text_input(
            "Password", placeholder="Enter Your Password", type="password"
        )
        password2 = st.text_input(
            "Password",
            placeholder="Confirm Your Password",
            type="password",
        )

        if email:
            if validate_email(email):
                if email not in get_user_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        # Add User to DB
                                        hashed_password = stauth.Hasher(
                                            [password2]
                                        ).generate()
                                        insert_user(email, username, hashed_password[0])
                                        st.success("Account created successfully!!")
                                        st.balloons()
                                    else:
                                        st.warning("Passwords Do Not Match")
                                else:
                                    st.warning("Password is too Short")
                            else:
                                st.warning("Username Too short")
                        else:
                            st.warning("Username Already Exists")

                    else:
                        st.warning("Invalid Username")
                else:
                    st.warning("Email Already exists!!")
            else:
                st.warning("Invalid Email")

        st.form_submit_button("Sign Up")
