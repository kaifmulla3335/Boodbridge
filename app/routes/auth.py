from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Hospital, BloodBank, Donor
from urllib.parse import urlparse

bp = Blueprint('auth', __name__)

def redirect_based_on_user_type(user):
    """Redirect user to their respective dashboard based on user type"""
    if user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.user_type == 'blood_bank':
        return redirect(url_for('blood_bank.dashboard'))  # ← FIXED
    elif user.user_type == 'donor':
        return redirect(url_for('donor.dashboard'))
    elif user.user_type == 'hospital':
        return redirect(url_for('hospital.dashboard'))
    else:
        return redirect(url_for('main.index'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_based_on_user_type(current_user)
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=request.form.get('remember_me'))
        next_page = request.args.get('next')
        if next_page and urlparse(next_page).netloc == '':
            return redirect(next_page)
        
        return redirect_based_on_user_type(user)
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type):
    if current_user.is_authenticated:
        return redirect_based_on_user_type(current_user)
    
    if user_type not in ['donor', 'hospital', 'blood_bank']:
        flash('Invalid user type', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register', user_type=user_type))
        
        if user_type == 'donor':
            user = Donor(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
                blood_type=request.form.get('blood_type')
            )
        elif user_type == 'hospital':
            user = Hospital(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
                hospital_name=request.form.get('hospital_name'),
                license_number=request.form.get('license_number'),
                emergency_contact=request.form.get('emergency_contact')
            )
        else:  # blood_bank
            user = BloodBank(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
                bank_name=request.form.get('bank_name'),
                license_number=request.form.get('license_number'),
                emergency_contact=request.form.get('emergency_contact')
            )
        
        user.user_type = user_type  # ← ADD THIS LINE - Important!
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template(f'auth/register_{user_type}.html', user_type=user_type)