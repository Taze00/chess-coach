"""
Authentication blueprint for user registration, login, and logout.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        chesscom_username = request.form.get('chesscom_username')

        # Validation
        if not email or not password or not chesscom_username:
            flash('Alle Felder sind erforderlich.', 'danger')
            return render_template('register.html')

        if password != password_confirm:
            flash('Passwörter stimmen nicht überein.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Passwort muss mindestens 6 Zeichen lang sein.', 'danger')
            return render_template('register.html')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email bereits registriert.', 'danger')
            return render_template('register.html')

        # Create new user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email,
            password_hash=password_hash,
            chesscom_username=chesscom_username
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account erfolgreich erstellt! Bitte einloggen.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        # Validation
        if not email or not password:
            flash('Email und Passwort sind erforderlich.', 'danger')
            return render_template('login.html')

        # Find user
        user = User.query.filter_by(email=email).first()

        # Check password
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash('Ungültige Email oder Passwort.', 'danger')
            return render_template('login.html')

        # Login user
        login_user(user, remember=remember)

        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('index'))
