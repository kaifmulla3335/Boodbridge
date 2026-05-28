from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Donation, Donor, BloodDrive, DriveRegistration
from datetime import datetime, timedelta

bp = Blueprint('donor', __name__, url_prefix='/donor')
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'donor':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    # Get donor's pending donations
    pending_donations = Donation.query.filter(
        Donation.donor_id == current_user.id,
        Donation.status == 'PENDING'
    ).order_by(Donation.created_at.desc()).all()

    accepted_donations = Donation.query.filter(
        Donation.donor_id == current_user.id,
        Donation.status == 'ACCEPTED'
    ).order_by(Donation.donation_date.desc()).all()

    rejected_donations = Donation.query.filter(
        Donation.donor_id == current_user.id,
        Donation.status == 'REJECTED'
    ).order_by(Donation.created_at.desc()).all()

    recent_completed_donations = Donation.query.filter_by(
        donor_id=current_user.id,
        status='COMPLETED'
    ).order_by(Donation.donation_date.desc()).limit(5).all()

    # Get registered blood drives
    registered_drives = []
    registrations = DriveRegistration.query.filter_by(donor_id=current_user.id).all()
    for reg in registrations:
        drive = BloodDrive.query.get(reg.drive_id)
        if drive:
            registered_drives.append(drive)

    return render_template('main/donor_dashboard.html',
                           pending_donations=pending_donations,
                           accepted_donations=accepted_donations,
                           rejected_donations=rejected_donations,
                           recent_completed_donations=recent_completed_donations,
                           registered_drives=registered_drives)
@bp.route('/profile')
@login_required
def profile():
    if current_user.user_type != 'donor':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    # Get donation history
    donations = Donation.query.filter_by(donor_id=current_user.id)\
        .order_by(Donation.donation_date.desc()).all()
    
    # Get registered blood drives
    registered_drives = DriveRegistration.query.filter_by(
        donor_id=current_user.id,
        status='registered'
    ).join(BloodDrive).order_by(BloodDrive.start_date).all()
    
    return render_template('donor/profile.html',
                         donations=donations,
                         registered_drives=registered_drives)

@bp.route('/donation-history')
@login_required
def donation_history():
    if current_user.user_type != 'donor':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    donations = Donation.query.filter_by(donor_id=current_user.id)\
        .order_by(Donation.donation_date.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('donor/donation_history.html', donations=donations)

@bp.route('/register-drive/<int:drive_id>', methods=['POST'])
@login_required
def register_for_drive(drive_id):
    if current_user.user_type != 'donor':
        flash('Only donors can register for blood drives.', 'error')
        return redirect(url_for('main.index'))
    
    drive = BloodDrive.query.get_or_404(drive_id)
    
    # Check if already registered
    existing_registration = DriveRegistration.query.filter_by(
        donor_id=current_user.id,
        drive_id=drive_id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this blood drive.', 'info')
        return redirect(url_for('main.blood_drive_detail', id=drive_id))
    
    # Create new registration
    registration = DriveRegistration(
        donor_id=current_user.id,
        drive_id=drive_id,
        status='registered',
        notes=request.form.get('notes', '')
    )
    
    try:
        db.session.add(registration)
        db.session.commit()
        flash('Successfully registered for the blood drive!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error registering for blood drive: {str(e)}', 'error')
    
    return redirect(url_for('main.blood_drive_detail', id=drive_id))

@bp.route('/cancel-registration/<int:registration_id>', methods=['POST'])
@login_required
def cancel_registration(registration_id):
    if current_user.user_type != 'donor':
        flash('Only donors can cancel registrations.', 'error')
        return redirect(url_for('main.index'))
    
    registration = DriveRegistration.query.get_or_404(registration_id)
    
    # Verify ownership
    if registration.donor_id != current_user.id:
        flash('You can only cancel your own registrations.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        registration.status = 'cancelled'
        db.session.commit()
        flash('Registration cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling registration: {str(e)}', 'error')
    
    return redirect(url_for('main.blood_drive_detail', id=registration.drive_id))