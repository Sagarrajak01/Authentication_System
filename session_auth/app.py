import streamlit as st
import secrets
import sqlite3
import bcrypt
from datetime import datetime

DATABASE = "users.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL
        )
    """)

    conn.commit()
    conn.close()

initialize_database()

def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

def verify_password(password, stored_hash):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    )

def register_user(username, password):

    if username.strip() == "" or password == "":
        return False, "Username and Password are required."

    hashed_password = hash_password(password)

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        print("\n========== USER REGISTERED ==========")
        print("Username :", username)
        print("Stored Password Hash :")
        print(hashed_password.decode())

        return True, hashed_password.decode()

    except sqlite3.IntegrityError:
        return False, "Username already exists."

def login_user(username, password):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return False

    stored_hash = row[0]

    if verify_password(password, stored_hash):

        st.session_state.session_id = secrets.token_hex(16)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.login_time = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        print("\n========== SESSION CREATED ==========")
        print("Session ID :", st.session_state.session_id)
        print(dict(st.session_state))

        return True

    return False


def validate_session():

    return (
        "logged_in" in st.session_state and
        st.session_state.logged_in
    )


def logout_user():

    print("\n========== SESSION DESTROYED ==========")

    if "session_id" in st.session_state:
        print("Session ID :", st.session_state.session_id)

    print(dict(st.session_state))

    st.session_state.clear()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.set_page_config(
    page_title="Session-Based Authentication",
    page_icon="",
    layout="centered"
)

st.title("Session-Based Authentication System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Register", "Login", "Dashboard"]
)


if menu == "Register":

    st.header("User Registration")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Register"):

        success, message = register_user(
            username,
            password
        )

        if success:
            st.success("User Registered Successfully")
            st.write("Stored Password Hash")
            st.code(message)
        else:
            st.error(message)


elif menu == "Login":

    st.header("User Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if login_user(username, password):
            st.success("Authentication Successful")
            st.rerun()
        else:
            st.error("Invalid Username or Password")


elif menu == "Dashboard":

    if validate_session():

        st.header("Dashboard")

        st.success("Session Active")

        st.write("### Welcome,", st.session_state.username)

        st.write("**Current Username:**")
        st.write(st.session_state.username)

        st.write("**Login Time:**")
        st.write(st.session_state.login_time)

        st.write("**Session ID:**")
        st.code(st.session_state.session_id)

        st.write("**Authentication Status:**")
        st.success("Active")

        st.write("### Session Variables")

        st.json(dict(st.session_state))

        if st.button("Logout"):

            logout_user()

            st.success(
                "Session terminated successfully."
            )

            st.rerun()

    else:
        st.error("Access Denied. Please login first.")
        st.info("Please go to the Login page from the sidebar.")