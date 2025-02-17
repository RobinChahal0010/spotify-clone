from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import base64
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Flask app setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")

# ✅ Database, authentication & encryption setup
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ✅ User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🎵 **Home Route**
@app.route("/")
def home():
    return render_template("home.html", user=current_user)

# 🔐 **Signup Route**
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        # ✅ Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists. Try logging in.", "danger")
            return redirect(url_for("login"))

        # ✅ Save user to DB
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# 🔐 **Login Route**
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials, please try again.", "danger")

    return render_template("login.html")

# 🏠 **Dashboard (For Logged-in Users)**
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

# 🚪 **Logout Route**
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# ✅ **Spotify API Integration**
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=data, headers=headers)
    token_data = response.json()
    return token_data.get("access_token")

def get_popular_artists(limit=4):
    token = get_spotify_token()
    if not token:
        return []

    url = "https://api.spotify.com/v1/browse/new-releases"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("albums", {}).get("items", [])
        return [{"name": album["artists"][0]["name"], "image": album["images"][0]["url"]} for album in data[:limit]]

    return []

@app.route("/popular_artists", methods=["GET"])
def popular_artists_route():
    return jsonify({"artists": get_popular_artists()})

@app.route("/all_artists", methods=["GET"])
def all_artists_route():
    return render_template("all_artists.html", artists=get_popular_artists(limit=20))

# ✅ **Audius API Integration**
AUDIUS_API_URL = os.getenv("AUDIUS_API_URL", "https://discoveryprovider.audius.co")

def get_trending_songs(limit=4):
    url = f"{AUDIUS_API_URL}/v1/tracks/trending"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("data", [])
        return [{"title": song["title"], "artist": song["user"]["name"], "artwork": song.get("artwork", {}).get("1000x1000", "static/default.jpg")} for song in data[:limit]]

    return []

@app.route("/trending_songs", methods=["GET"])
def trending_songs_route():
    return jsonify({"songs": get_trending_songs()})

@app.route("/all_songs", methods=["GET"])
def all_songs_route():
    return render_template("all_songs.html", songs=get_trending_songs(limit=20))

# ✅ **Error Handling**
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500

# ✅ **Initialize Database**
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

