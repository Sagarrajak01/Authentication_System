import streamlit as st
import requests

API = "http://127.0.0.1:5000"

if "jwt" not in st.session_state:
    st.session_state.jwt = ""

st.title("JWT Authentication Lab")

menu = st.sidebar.radio(
    "Menu",
    ["Register", "Login", "Profile"]
)

if menu == "Register":

    st.header("Register")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Register"):

        r = requests.post(
            API + "/register",
            json={
                "username": user,
                "password": pwd
            }
        )

        st.json(r.json())


elif menu == "Login":

    st.header("Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        r = requests.post(
            API + "/login",
            json={
                "username": user,
                "password": pwd
            }
        )

        if r.status_code == 200:

            token = r.json()["token"]

            st.session_state.jwt = token

            st.success("Authentication Successful")

            st.write("Generated JWT")

            st.code(token)

        else:
            st.error(r.json()["message"])


else:

    st.header("Protected API")

    if st.session_state.jwt == "":
        st.warning("Please Login First")

    else:

        st.write("Stored JWT")

        st.code(st.session_state.jwt)

        if st.button("Access Protected API"):

            r = requests.get(
                API + "/profile",
                headers={
                    "Authorization":
                    "Bearer " + st.session_state.jwt
                }
            )

            st.json(r.json())

        if st.button("Logout"):

            st.session_state.jwt = ""

            st.success("Logged Out")