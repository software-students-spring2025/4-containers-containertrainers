"""App"""

import os
import glob
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import db

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
RECORDINGS_FOLDER = '/app/recordings'
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)

# look for the next file, file numbers are sequential
def get_next_file_number():
    """this gets the next file number"""
    existing_files = glob.glob(os.path.join(RECORDINGS_FOLDER, "recording_*webm"))
    # if no recordings
    if not existing_files:
        return 1
    numbers = []
    for filename in existing_files:
        try:
            base = os.path.basename(filename)
            num_str = base.split('_')[1].split('.')[0]
            numbers.append(int(num_str))
        except (IndexError, ValueError):
            continue

    return max(numbers) + 1 if numbers else 1

#main page
@app.route('/record')
def index():
    """ flask render the main page"""
    return render_template('record.html')

# uploads to the volume
@app.route('/upload', methods=['POST'])
def upload_audio():
    """see if the file is in the resquest get the file into the volume"""
    if 'audio' not in request.files:
        return jsonify({'success': False})

    audio_file = request.files['audio']

    next_number = get_next_file_number()

    filename = f"recording_{next_number}.webm"

    filepath = os.path.join(RECORDINGS_FOLDER, filename)
    audio_file.save(filepath)

    return jsonify({'success':True, 'filename': filename})



if __name__ == "__main__":
    PORT = os.getenv("PORT")
    app.run(host="0.0.0.0", port=3000)
