from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt
from datetime import datetime

app = Flask(__name__)

# Secret key used to sign Flask sessions
app.secret_key = "lab_session_secret_key"

DATABASE = "users.db"


# --------------------------------------------------
# Initialize Database
# --------------------------------------------------
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


# --------------------------------------------------
# Hash Password
# --------------------------------------------------
def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )


# --------------------------------------------------
# Verify Password
# --------------------------------------------------
def verify_password(password, stored_hash):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    )


# --------------------------------------------------
# Home
# --------------------------------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))


# --------------------------------------------------
# Register User
# --------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if username == "" or password == "":
            message = "Username and Password are required."
            return render_template("register.html", message=message)

        hashed_password = hash_password(password)

        try:

            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            print("\n========== USER REGISTERED ==========")
            print("Username :", username)
            print("Password Hash :", hashed_password.decode())

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            message = "Username already exists."

    return render_template(
        "register.html",
        message=message
    )


# --------------------------------------------------
# Login
# --------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    message = request.args.get("message", "")

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:
            message = "Invalid username or password."

        else:

            stored_hash = row[0]

            if verify_password(password, stored_hash):

                session.clear()

                session["username"] = username
                session["logged_in"] = True
                session["login_time"] = datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                print("\n========== SESSION CREATED ==========")
                print("Session Data:")
                print(dict(session))

                return redirect(url_for("dashboard"))

            else:
                message = "Invalid username or password."

    return render_template(
        "login.html",
        message=message
    )


# --------------------------------------------------
# Protected Dashboard
# --------------------------------------------------
@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect(url_for("unauthorized"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        login_time=session.get("login_time"),
        session_data=dict(session),
        authentication_status="Active"
    )


# --------------------------------------------------
# Unauthorized Page
# --------------------------------------------------
@app.route("/unauthorized")
def unauthorized():
    return render_template("unauthorized.html")


# --------------------------------------------------
# Logout
# --------------------------------------------------
@app.route("/logout")
def logout():

    print("\n========== SESSION DESTROYED ==========")
    print("Session Data:")
    print(dict(session))

    session.clear()

    return redirect(
        url_for(
            "login",
            message="Session terminated successfully."
        )
    )


# --------------------------------------------------
# Run Application
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)