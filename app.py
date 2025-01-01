from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from functools import wraps
import datetime

# Initialize the Flask application
app = Flask(__name__)

# Set the secret key for session management
app.secret_key = "9857469848689457689458976"

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Pentesting"

# Initialize MongoDB
mongo = PyMongo(app)



@app.route('/')
def index():
    """Render the homepage."""
    if 'user_id' in session:
        user = mongo.db.Users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('index.html', logged_in=True, user=user)
    return render_template('index.html', logged_in=False)


@app.route('/contact')
def contact(): 

    return render_template('contact.html')
@app.route('/unauthorized')
def unauthorized():
    """Render the 401 Unauthorized Access page."""
    return render_template('401.html'), 401


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if the user is not logged in
            return redirect(url_for('unauthorized'))  # Redirect to the 401 page
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        "total_scans": 50,
        "completed_scans": 45,
        "pending_scans": 5,
        "severe_threats": 12,
        "medium_low_threats": 30,
        "security_score": 85,
        "score_improvement": 5
    }
    threat_stats = {
        "critical": 5,
        "high": 7,
        "medium": 20,
        "low": 10
    }
    timeline_labels = ["Jan", "Feb", "Mar", "Apr", "May"]
    timeline_data = [10, 15, 20, 25, 30]

    return render_template(
        'dashboard.html',
        stats=stats,
        threat_stats=threat_stats,
        timeline_labels=timeline_labels,
        timeline_data=timeline_data
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if user is not logged in
            flash("You need to log in to access this page.", "warning")  # Optional flash message
            return redirect(url_for('unauthorized'))  # Redirect to unauthorized page
        return f(*args, **kwargs)
    return decorated_function

@app.route('/scan')
@login_required
def scanning(): 

    return render_template('scanning.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('login'))

        try:
            user = mongo.db.Users.find_one({"email": email})
            if user and check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['user_name'] = user['name']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password. Please try again.", "danger")
        except Exception as e:
            flash("An error occurred. Please try again later.", "danger")
            print(f"Error logging in: {e}")

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        try:
            existing_user = mongo.db.Users.find_one({"email": email})
            if existing_user:
                flash("Email is already registered!", "danger")
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)
            mongo.db.Users.insert_one({
                "name": name,
                "email": email,
                "password": hashed_password,
                "created_at": datetime.datetime.utcnow()
            })
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("An error occurred while registering. Please try again.", "danger")
            print(f"Error inserting user into MongoDB: {e}")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Log out the user."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """Render the profile page."""
    if 'user_id' not in session:
        flash("Please log in to access your profile.", "danger")
        return redirect(url_for('login'))

    try:
        user = mongo.db.Users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('profile_dynamic.html', user=user)
    except Exception as e:
        flash("An error occurred while accessing your profile.", "danger")
        print(f"Error fetching user from MongoDB: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
