from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

# --- EXISTING LOGIN & REGISTER ROUTES ---
@auth.route('/login')
def login():
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    login_user(user)
    return redirect(url_for('main.dashboard'))

@auth.route('/register')
def register():
    return render_template('auth/register.html')

@auth.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    if password != confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('auth.register'))
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.register'))
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
    db.session.add(new_user)
    db.session.commit()
    flash('Registration successful! Please login.')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# --- NEW FORGOT PASSWORD ROUTES ---

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        # Check if a user exists with BOTH the email and name
        user = User.query.filter_by(email=email, name=name).first()
        
        if user:
            # If user is found, redirect to the page where they can set a new password
            return redirect(url_for('auth.reset_password', user_id=user.id))
        else:
            # If no match, deny access
            flash('No account found with that name and email address.')
            return redirect(url_for('auth.forgot_password'))
            
    return render_template('auth/forgot_password.html')


@auth.route('/reset-password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('auth.reset_password', user_id=user.id))

        # Update the user's password with the new hashed password
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()

        flash('Your password has been reset successfully! Please login.')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', user_id=user.id)