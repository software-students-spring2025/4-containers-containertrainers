"""App"""
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import db

app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/')
def home():
    """Home Route"""
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup Route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not (username and password):
            return render_template('index.html', message="All fields are required")
        if db.accounts.find_one({'username': username}):
            return render_template('index.html',
                                   message="Account with this username already created.")
        hashed_password = generate_password_hash(password)
        new_user = {
            '_id': ObjectId(),
            'username': username,
            'password': hashed_password
        }
        db.accounts.insert_one(new_user)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.accounts.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('profile'))

        return render_template('index.html', message="Invalid username or password")
    return render_template('login.html')


@app.route('/profile')
def profile():
    """Profile Route"""
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        user = db.accounts.find_one({'_id': user_id})
        username = user['username']
        return render_template('profile.html', username=username)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Logout Route"""
    session.clear()
    return render_template('index.html')


if __name__ == '__main__':
    PORT = os.getenv('PORT')
    app.run(host='0.0.0.0', port=3000)
