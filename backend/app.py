from flask import Flask, render_template, request, redirect, session
import sqlite3
from database import create_tables
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")
app.secret_key = "secret123"   # for sessions

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        hashed_password = generate_password_hash(data["password"])

        conn = sqlite3.connect("health.db")
        conn.execute("""
        INSERT INTO users 
        (name, age, gender, diseases, medicines, email, password)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["age"],
            data["gender"],
            data["diseases"],
            data["medicines"],
            data["email"],
            hashed_password
        ))
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("health.db")
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user[7], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return "<h2>Welcome to your Health Dashboard</h2>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
