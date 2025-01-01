from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import mongo  # Import the initialized mongo object
import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Debugging
        print(f"Received data - Name: {name}, Email: {email}, Password: {password}")

        # Validation checks
        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.register'))

        # Check if the email already exists
        try:
            existing_user = mongo.db.Users.find_one({"email": email})  # Access Users collection
            if existing_user:
                flash("Email is already registered!", "danger")
                return redirect(url_for('auth.register'))

            # Insert new user into the database
            hashed_password = generate_password_hash(password)
            mongo.db.Users.insert_one({
                "name": name,
                "email": email,
                "password": hashed_password,
                "created_at": datetime.datetime.utcnow()
            })

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("An error occurred while registering. Please try again.", "danger")
            print(f"Error accessing MongoDB: {e}")
            return redirect(url_for('auth.register'))

    return render_template('register.html')
