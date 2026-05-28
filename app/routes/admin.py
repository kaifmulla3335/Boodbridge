from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, BloodRequest, Donation, BloodInventory, Hospital, Donor, BloodDrive, BloodBank
from app.forms import ApproveRejectForm, BloodDriveForm
from functools import wraps
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get pending blood requests
    pending_requests = BloodRequest.query.filter_by(status='PENDING').order_by(BloodRequest.created_at.desc()).all()
    
    # Get ACTIVE blood requests (visible on landing page)
    active_requests = BloodRequest.query.filter_by(status='ACTIVE').order_by(BloodRequest.created_at.desc()).all()
    
    # Get pending donations
    pending_donations = Donation.query.filter_by(status='PENDING').order_by(Donation.created_at.desc()).all()
    
    # Get all blood requests for the table
    blood_requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()
    
    # Get all donations for the table
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    
    # Get total donors
    total_donors = Donor.query.count()

    blood_drives = BloodDrive.query.order_by(BloodDrive.start_date.desc()).all()
    form = ApproveRejectForm()
    
    # Debug print
    print(f"Admin Dashboard - Pending Requests: {len(pending_requests)}")
    print(f"Admin Dashboard - Active Requests: {len(active_requests)}")
    for req in pending_requests:
        print(f"  - Request ID: {req.id}, Blood: {req.blood_type}, Hospital: {req.hospital_id}")
    
    return render_template('admin/dashboard.html', 
                           pending_requests=pending_requests,
                           active_requests=active_requests,
                           pending_donations=pending_donations, 
                           blood_requests=blood_requests,
                           donations=donations,
                           total_donors=total_donors, 
                           blood_drives=blood_drives,
                           form=form)

@bp.route('/blood-request/<int:request_id>/<action>', methods=['POST'])
@login_required
@admin_required
def manage_blood_request(request_id, action):
    blood_request = BloodRequest.query.get_or_404(request_id)
    admin_notes = request.form.get('admin_notes', '')
    
    if action == 'accept':
        # Check if enough blood is available
        blood_inventory = BloodInventory.query.filter_by(blood_type=blood_request.blood_type).first()
        
        if not blood_inventory or blood_inventory.units_available < blood_request.units_needed:
            flash(f'Not enough {blood_request.blood_type} blood available in inventory!', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Deduct from inventory
        blood_inventory.units_available -= blood_request.units_needed
        blood_request.status = 'ACCEPTED'
        blood_request.admin_notes = admin_notes
        flash(f'Blood request #{request_id} has been ACCEPTED. Inventory updated.', 'success')
        
    elif action == 'fulfill':
        # Mark as fulfilled (completed)
        blood_request.status = 'FULFILLED'
        blood_request.admin_notes = admin_notes
        flash(f'Blood request #{request_id} has been FULFILLED.', 'success')
        
    elif action == 'reject':
        # If rejecting an ACTIVE request, return inventory
        if blood_request.status == 'ACTIVE':
            blood_inventory = BloodInventory.query.filter_by(blood_type=blood_request.blood_type).first()
            if blood_inventory:
                blood_inventory.units_available += blood_request.units_needed
        blood_request.status = 'REJECTED'
        blood_request.admin_notes = admin_notes
        flash(f'Blood request #{request_id} has been REJECTED.', 'warning')
    else:
        flash('Invalid action', 'error')
        return redirect(url_for('admin.dashboard'))
    
    blood_request.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/donation/<int:donation_id>/<action>', methods=['POST'])
@login_required
@admin_required
def manage_donation(donation_id, action):
    donation = Donation.query.get_or_404(donation_id)
    admin_notes = request.form.get('admin_notes', '')
    
    if action == 'accept':
        # Add to inventory
        blood_inventory = BloodInventory.query.filter_by(blood_type=donation.blood_type).first()
        
        if blood_inventory:
            blood_inventory.units_available += donation.units
        else:
            # Create new inventory entry
            blood_inventory = BloodInventory(
                blood_type=donation.blood_type,
                units_available=donation.units
            )
            db.session.add(blood_inventory)
        
        donation.status = 'ACCEPTED'
        donation.admin_notes = admin_notes
        flash(f'Donation #{donation_id} has been ACCEPTED. Inventory updated.', 'success')
        
    elif action == 'reject':
        donation.status = 'REJECTED'
        donation.admin_notes = admin_notes
        flash(f'Donation #{donation_id} has been REJECTED.', 'warning')
    else:
        flash('Invalid action', 'error')
        return redirect(url_for('admin.dashboard'))
    
    donation.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/schedule_drive', methods=['GET', 'POST'])
@login_required
@admin_required
def schedule_drive():
    form = BloodDriveForm()
    if form.validate_on_submit():
        new_drive = BloodDrive(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            organizer_id=current_user.id,
            status='scheduled'
        )
        db.session.add(new_drive)
        db.session.commit()
        flash('Blood drive scheduled successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/schedule_drive.html', form=form)

@bp.route('/edit_drive/<int:drive_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_drive(drive_id):
    drive = BloodDrive.query.get_or_404(drive_id)
    form = BloodDriveForm(obj=drive)
    if form.validate_on_submit():
        drive.title = form.title.data
        drive.description = form.description.data
        drive.location = form.location.data
        drive.start_date = form.start_date.data
        drive.end_date = form.end_date.data
        db.session.commit()
        flash('Blood drive updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/schedule_drive.html', form=form, drive=drive)

@bp.route('/delete_drive/<int:drive_id>', methods=['POST'])
@login_required
@admin_required
def delete_drive(drive_id):
    drive = BloodDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash('Blood drive deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))