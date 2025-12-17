from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from utils.weather_api import get_weather

app = Flask(__name__)
app.secret_key = "supersecretkey123"


# --------------------- DATABASE SETUP ---------------------
def create_tables():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        make TEXT,
        model TEXT,
        year INTEGER,
        mileage INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        service_type TEXT,
        service_date TEXT,
        mileage INTEGER,
        cost REAL,
        notes TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
    );
    """)

    conn.commit()
    conn.close()


create_tables()


# --------------------- AUTH ROUTES ---------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Email already exists."

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# --------------------- DASHBOARD ---------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM vehicles WHERE user_id=?", (user_id,))
    vehicles = c.fetchall()

    conn.close()

    weather = get_weather("New York")  # you can replace location

    return render_template("dashboard.html", vehicles=vehicles, weather=weather)


# --------------------- VEHICLES ---------------------
@app.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():
    if request.method == "POST":
        make = request.form["make"]
        model = request.form["model"]
        year = request.form["year"]
        mileage = request.form["mileage"]
        user_id = session["user_id"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO vehicles (user_id, make, model, year, mileage) VALUES (?, ?, ?, ?, ?)",
                  (user_id, make, model, year, mileage))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_vehicle.html")


# --------------------- MAINTENANCE ---------------------
@app.route("/add_maintenance/<int:vehicle_id>", methods=["GET", "POST"])
def add_maintenance(vehicle_id):
    if request.method == "POST":
        service_type = request.form["service_type"]
        service_date = request.form["service_date"]
        mileage = request.form["mileage"]
        cost = request.form["cost"]
        notes = request.form["notes"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""
        INSERT INTO maintenance (vehicle_id, service_type, service_date, mileage, cost, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (vehicle_id, service_type, service_date, mileage, cost, notes))

        conn.commit()
        conn.close()

        return redirect("/maintenance_history/" + str(vehicle_id))

    return render_template("add_maintenance.html", vehicle_id=vehicle_id)


@app.route("/maintenance_history/<int:vehicle_id>")
def maintenance_history(vehicle_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM maintenance WHERE vehicle_id=?", (vehicle_id,))
    logs = c.fetchall()
    conn.close()

    return render_template("maintenance_history.html", logs=logs)
    

if __name__ == "__main__":
    app.run(debug=True)
