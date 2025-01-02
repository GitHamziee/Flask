from flask import Flask, render_template, request, redirect, url_for, flash, session , jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from functools import wraps
import os
import datetime
from zap_scanner import ZAPScanner
from scheduled_scans import scheduler  # Import the scheduler logic

zap_scanner = ZAPScanner()  # Initialize the scanner


# Initialize the Flask application
app = Flask(__name__)



# Set the secret key for session management
app.secret_key = "9857469848689457689458976"

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Pentesting"

# Initialize MongoDB
mongo = PyMongo(app)



# Helper function for login-required routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to log in to access this page.", "warning")
            return redirect(url_for('unauthorized'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        user = mongo.db.Users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('index.html', logged_in=True, user=user)
    return render_template('index.html', logged_in=False)
@app.route('/schedule_scan', methods=['POST'])
@login_required
def schedule_scan():
    """Schedule a scan."""
    url = request.form.get('url')
    scan_type = request.form.get('scan_type')
    max_depth = int(request.form.get('max_depth', 5)) if scan_type == 'spider' else None
    schedule_time = datetime.datetime.strptime(request.form.get('schedule_time'), '%Y-%m-%dT%H:%M')

    # Save to ScheduledScans collection
    mongo.db.ScheduledScans.insert_one({
        "user_id": ObjectId(session['user_id']),
        "url": url,
        "scan_type": scan_type,
        "max_depth": max_depth,
        "schedule_time": schedule_time,
        "status": "pending",
        "result": None,
        "created_at": datetime.datetime.utcnow()
    })

    flash("Scan scheduled successfully!", "success")
    return redirect(url_for('scan'))

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if request.method == 'POST':
        # Retrieve form data
        url = request.form.get('url')
        scan_type = request.form.get('scan_type')
        max_depth = int(request.form.get('max_depth', 5))

        # Perform scan
        try:
            if scan_type == 'spider':
                result = zap_scanner.spider_scan(url, max_depth)
            elif scan_type == 'active':
                result = zap_scanner.active_scan(url)
            elif scan_type == 'comprehensive':
                result = zap_scanner.comprehensive_scan(url)
            else:
                result = {"error": "Invalid scan type selected"}

            # Check for errors in the result
            if "error" in result:
                flash(f"Scan failed: {result['error']}", "danger")
                return redirect(url_for('scan'))

            # Save the valid result to the database
            mongo.db.Scans.insert_one({
                "user_id": ObjectId(session['user_id']),
                "url": url,
                "scan_type": scan_type,
                "max_depth": max_depth,
                "result": result,
                "timestamp": datetime.datetime.utcnow()
            })

            # Render results.html with the scan results
            return render_template('results.html', result=result, url=url)
        except Exception as e:
            flash(f"An error occurred during scanning: {e}", "danger")
            return redirect(url_for('scan'))

    return render_template('scanning.html')



@app.route('/unauthorized')
def unauthorized():
    return render_template('401.html'), 401

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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = mongo.db.Users.find_one({'_id': ObjectId(user_id)})

    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        bio = request.form.get('bio').strip()
        profile_image = request.files.get('profile-image')

        update_data = {
            "name": name,
            "email": email,
            "bio": bio
        }

        if profile_image and profile_image.filename:
            image_directory = os.path.join('static', 'images', 'profiles')
            os.makedirs(image_directory, exist_ok=True)
            image_path = os.path.join(image_directory, profile_image.filename)
            profile_image.save(image_path)
            update_data["profile_image"] = f'images/profiles/{profile_image.filename}'

        mongo.db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        session['user_name'] = name
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('profile_dynamic.html', user=user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Handle profile updates."""
    try:
        # Fetch the logged-in user's ID
        user_id = session.get('user_id')
        if not user_id:
            flash("Unauthorized access!", "danger")
            return redirect(url_for('login'))

        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        bio = request.form.get('bio')
        profile_image = request.files.get('profile-image')

        # Update the user record
        update_data = {
            "name": name,
            "email": email,
            "bio": bio,
        }

        # If a profile image is uploaded, save it and store the filename
        if profile_image:
            filename = f"{user_id}_profile.png"
            profile_image.save(f"static/uploads/{filename}")
            update_data["profile_image"] = filename

        # Update the database
        mongo.db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    except Exception as e:
        flash("An error occurred while updating your profile. Please try again.", "danger")
        print(f"Error updating profile: {e}")
        return redirect(url_for('profile'))



@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user_id = session['user_id']
    current_password = request.form.get('current-password')
    new_password = request.form.get('new-password')
    confirm_new_password = request.form.get('confirm-new-password')

    user = mongo.db.Users.find_one({'_id': ObjectId(user_id)})

    if not check_password_hash(user['password'], current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for('profile'))

    if new_password != confirm_new_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('profile'))

    hashed_password = generate_password_hash(new_password)
    mongo.db.Users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password}}
    )

    flash("Password updated successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = session['user_id']
    mongo.db.Users.delete_one({"_id": ObjectId(user_id)})
    session.clear()
    flash("Your account has been deleted.", "success")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user = mongo.db.Users.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

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

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
