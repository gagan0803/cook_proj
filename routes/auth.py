from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from forms import LoginForm, RegisterForm, PreferencesForm
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.get_by_username(form.username.data):
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.get_by_email(form.email.data):
            flash('Email already registered. Please use a different email or login.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if user:
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error creating account. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    preferences = current_user.get_preferences()
    form = PreferencesForm(obj=preferences)
    
    if form.validate_on_submit():
        new_preferences = {
            'vegetarian': form.vegetarian.data,
            'vegan': form.vegan.data,
            'gluten_free': form.gluten_free.data,
            'dairy_free': form.dairy_free.data
        }
        
        if current_user.update_preferences(new_preferences):
            flash('Preferences updated successfully!', 'success')
        else:
            flash('Error updating preferences.', 'danger')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form)
