import os
import db
from flask import Flask, render_template, request, redirect, abort, url_for, make_response, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not (username and password):
            return render_template('index.html', message="All fields are required")
        if db.accounts.find_one({username: username}):
            return render_template('index.html', message="Account with this username already created.")
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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.accounts.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('profile'))
        else:
            return render_template('index.html', message="Invalid username or password")
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')



if __name__ == '__main__':
    PORT = os.getenv('PORT')
    app.run(host='0.0.0.0', port=3000)