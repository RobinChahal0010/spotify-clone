import os
import base64
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

# Views

def home(request):
    return render(request, "home.html", {"user": request.user})

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        if User.objects.filter(email=email).exists():
            messages.error(request, "User already exists. Try logging in.")
            return redirect("login")
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, email=email)
        messages.success(request, "Signup successful! Please log in.")
        return redirect("login")
    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard")
        except User.DoesNotExist:
            pass
        messages.error(request, "Invalid credentials, please try again.")
    return render(request, "login.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"user": request.user})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")

# Spotify API Integration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    return response.json().get("access_token")

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

def popular_artists_route(request):
    return JsonResponse({"artists": get_popular_artists()})

def all_artists_route(request):
    return render(request, "all_artists.html", {"artists": get_popular_artists(limit=20)})

# Audius API Integration
AUDIUS_API_URL = os.getenv("AUDIUS_API_URL", "https://discoveryprovider.audius.co")

def get_trending_songs(limit=4):
    url = f"{AUDIUS_API_URL}/v1/tracks/trending"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("data", [])
        return [{"title": song["title"], "artist": song["user"]["name"], "artwork": song.get("artwork", {}).get("1000x1000", "static/default.jpg")} for song in data[:limit]]
    return []

def trending_songs_route(request):
    return JsonResponse({"songs": get_trending_songs()})

def all_songs_route(request):
    return render(request, "all_songs.html", {"songs": get_trending_songs(limit=20)})

# Error Handling
from django.conf.urls import handler404, handler500

def page_not_found(request, exception):
    return render(request, "404.html", status=404)

def server_error(request):
    return render(request, "500.html", status=500)

handler404 = "myapp.views.page_not_found"
handler500 = "myapp.views.server_error"


