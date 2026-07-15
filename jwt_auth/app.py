from flask import Flask, request, jsonify
import sqlite3, bcrypt, jwt
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET = "jwt_secret"

conn = sqlite3.connect("users.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY,password BLOB)")

@app.post("/register")
def register():
    d = request.json
    try:
        conn.execute(
            "INSERT INTO users VALUES(?,?)",
            (d["username"], bcrypt.hashpw(d["password"].encode(), bcrypt.gensalt()))
        )
        conn.commit()
        return jsonify(message="User Registered")
    except:
        return jsonify(message="User Already Exists"), 400

@app.post("/login")
def login():
    d = request.json
    row = conn.execute(
        "SELECT password FROM users WHERE username=?",
        (d["username"],)
    ).fetchone()

    if row and bcrypt.checkpw(d["password"].encode(), row[0]):
        token = jwt.encode(
            {
                "username": d["username"],
                "exp": datetime.utcnow() + timedelta(minutes=10)
            },
            SECRET,
            algorithm="HS256"
        )
        return jsonify(token=token)

    return jsonify(message="Invalid Credentials"), 401

@app.get("/profile")
def profile():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return jsonify(message="Unauthorized"), 401

    try:
        payload = jwt.decode(
            auth.split()[1],
            SECRET,
            algorithms=["HS256"]
        )
        return jsonify(
            message="Authenticated",
            username=payload["username"]
        )
    except:
        return jsonify(message="Unauthorized"), 401

if __name__ == "__main__":
    app.run(debug=True)