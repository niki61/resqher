"""
ResQHer – app.py
Flask backend for authentication, contacts, location tracking, emergency alerts.
Deploy on PythonAnywhere (free).
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json, os, datetime

app = Flask(__name__)
CORS(app)  # Allow all origins so Vercel frontend can reach this

DB_FILE = "resqher_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "locations": [], "alerts": [], "events": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def ts():
    return datetime.datetime.utcnow().isoformat() + "Z"

def resp(data, status=200):
    return jsonify(data), status

# ── Health Check ──────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return resp({"status": "ResQHer backend running ✅", "time": ts()})

# ── Signup ────────────────────────────────────────
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return resp({"error": "All fields are required."}, 400)
    if len(password) < 6:
        return resp({"error": "Password must be at least 6 characters."}, 400)

    db = load_db()
    if email in db["users"]:
        return resp({"error": "An account with this email already exists."}, 409)

    db["users"][email] = {
        "name": name, "email": email,
        "password_hash": generate_password_hash(password),
        "created_at": ts(), "contacts": []
    }
    save_db(db)
    return resp({"message": "Account created successfully.", "name": name}, 201)

# ── Login ─────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    db = load_db()
    user = db["users"].get(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return resp({"error": "Invalid email or password."}, 401)

    return resp({"message": "Login successful.", "name": user["name"]})

# ── Contacts ──────────────────────────────────────
@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    email = request.args.get("user", "").lower()
    db = load_db()
    user = db["users"].get(email, {})
    return resp({"contacts": user.get("contacts", [])})

@app.route("/api/contacts", methods=["POST"])
def update_contacts():
    data     = request.get_json()
    email    = data.get("user", "").lower()
    contacts = data.get("contacts", [])
    db = load_db()
    if email in db["users"]:
        db["users"][email]["contacts"] = contacts
        save_db(db)
    return resp({"message": "Contacts updated."})

# ── Location ──────────────────────────────────────
@app.route("/api/location", methods=["POST"])
def store_location():
    data = request.get_json()
    db = load_db()
    entry = {
        "user":      data.get("user"),
        "lat":       data.get("lat"),
        "lng":       data.get("lng"),
        "accuracy":  data.get("accuracy"),
        "mapLink":   data.get("mapLink"),
        "timestamp": data.get("timestamp", ts())
    }
    db["locations"].append(entry)
    db["locations"] = db["locations"][-500:]
    save_db(db)
    return resp({"message": "Location stored."})

@app.route("/api/location", methods=["GET"])
def get_latest_location():
    email = request.args.get("user", "").lower()
    db = load_db()
    user_locs = [l for l in db["locations"] if l.get("user") == email]
    if not user_locs:
        return resp({"location": None})
    return resp({"location": user_locs[-1]})

# ── Emergency Alert ───────────────────────────────
@app.route("/api/alert", methods=["POST"])
def send_alert():
    data = request.get_json()
    db = load_db()
    alert = {
        "user":      data.get("user"),
        "name":      data.get("name"),
        "lat":       data.get("lat"),
        "lng":       data.get("lng"),
        "mapLink":   data.get("mapLink"),
        "contacts":  data.get("contacts", []),
        "timestamp": data.get("timestamp", ts()),
        "status":    "sent"
    }
    db["alerts"].append(alert)
    save_db(db)

    notified = []
    for c in alert["contacts"]:
        notified.append(f"{c['name']} ({c.get('phone', 'N/A')})")
        print(f"[ALERT] Notifying {c['name']} at {c.get('phone')} – EMERGENCY from {alert['name']}")

    print(f"[POLICE SIM] Alert for {alert['name']} at {alert['lat']},{alert['lng']}")
    return resp({"message": "Emergency alert dispatched.", "notified": notified, "police_notified": True})

# ── Event Log ─────────────────────────────────────
@app.route("/api/event", methods=["POST"])
def log_event():
    data = request.get_json()
    db = load_db()
    event = {
        "user":      data.get("user"),
        "event":     data.get("event"),
        "timestamp": data.get("timestamp", ts())
    }
    db["events"].append(event)
    db["events"] = db["events"][-200:]
    save_db(db)
    print(f"[EVENT] {event['user']} → {event['event']}")
    return resp({"message": "Event logged."})

if __name__ == "__main__":
    print("=" * 50)
    print("  ResQHer Backend – http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="127.0.0.1", port=5000)
