"""App"""

import os
import sys
import requests
import time
# import glob

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../machine-learning-client")
    )
)

# pylint: disable=import-error, wrong-import-position
# from client import process_audio

from pymongo import MongoClient

import db

from summarize_function import summarize_text_access


app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route("/")
def home():
    """Home Route"""
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Signup Route"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not (username and password):
            return render_template("index.html", message="All fields are required")
        if db.accounts.find_one({"username": username}):
            return render_template(
                "index.html", message="Account with this username already created."
            )
        hashed_password = generate_password_hash(password)
        new_user = {
            "_id": ObjectId(),
            "username": username,
            "password": hashed_password,
        }
        db.accounts.insert_one(new_user)
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login Route"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.accounts.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            return redirect(url_for("profile"))

        return render_template("index.html", message="Invalid username or password")
    return render_template("login.html")


@app.route("/profile")
def profile():
    """Profile Route"""
    if "user_id" in session:
        user_id = ObjectId(session["user_id"])
        user = db.accounts.find_one({"_id": user_id})
        username = user["username"]
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """Logout Route"""
    session.clear()
    return render_template("index.html")


# audio recording part
# RECORDINGS_FOLDER = "/app/recordings"
# os.makedirs(RECORDINGS_FOLDER, exist_ok=True)


# look for the next file, file numbers are sequential
def get_next_file_number():
    """this gets the next file number, the recording number should always be one greater"""
    # Find all recordings in the database
    recordings = list(db.recordings.find({}))

    # If no recordings
    if not recordings:
        return 1

    numbers = []
    for recording in recordings:
        try:
            filename = recording["filename"]
            num_str = filename.split("_")[1].split(".")[0]
            numbers.append(int(num_str))
        except (IndexError, ValueError):
            continue

    return max(numbers) + 1 if numbers else 1


# main page for recording
@app.route("/record")
def index():
    """flask render the main page"""
    return render_template("record.html")


# uploads to the mongodb in the database speech2text in recordings as a blob binary
@app.route("/upload", methods=["POST"])
def upload_audio():
    """see if the file is in the request and store it in the database speech2text,
    in recordings as a blob"""
    if "audio" not in request.files:
        return jsonify({"success": False})

    audio_file = request.files["audio"]

    next_number = get_next_file_number()

    filename = f"recording_{next_number}.webm"

    # Reads the binary data from the file which is recorded in webm format
    audio_data = audio_file.read()

    # Create a new record in the recordings collection
    # now not about file it is about db
    db.recordings.insert_one({"filename": filename, "audioData": audio_data})

    # audop data is a binary
    return jsonify({"success": True, "filename": filename})


@app.route("/result")
def get_result():
    """get resulting transcript and summary and return to front end"""

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        time.sleep(10)
        try:
            response = request.post('http://ml-client:5001/process_audio')
            if not response.ok:
                break
            retry_count += 1
            time.sleep(2)

        except requests.exceptions.RequestException:
            retry_count += 1
            time.sleep(2)


    # retrieve result not changed

    client = MongoClient("mongodb://mongodb:27017")
    speech_db = client["speech2text"]
    messages_collection = speech_db["messages"]

    latest_doc = messages_collection.find_one(sort=[("_id", -1)])

    transcript = latest_doc.get("transcript", "") if latest_doc else ""
    summary = latest_doc.get("summary", "") if latest_doc else ""

    return jsonify({"Transcript": transcript, "Summary": summary})


def summarized_text(sometext):
    """summarized text access funciton"""
    return summarize_text_access(sometext)


if __name__ == "__main__":
    PORT = os.getenv("PORT")
    app.run(host="0.0.0.0", port=3000)
