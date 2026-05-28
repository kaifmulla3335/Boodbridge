from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import BloodInventory, Donation, BloodDrive
from datetime import datetime, timedelta

bp = Blueprint('blood_bank', __name__, url_prefix='/blood-bank')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'blood_bank':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    all_blood_drives = BloodDrive.query.filter_by(
        organizer_id=current_user.id
    ).order_by(BloodDrive.start_date.desc()).all()
    
    total_drives = len(all_blood_drives)
    upcoming_drives = BloodDrive.query.filter(
        BloodDrive.organizer_id == current_user.id,
        BloodDrive.start_date > datetime.utcnow()
    ).count()
    total_donations = Donation.query.filter_by(
        status='COMPLETED'
    ).count()
    
    inventory = BloodInventory.query.filter_by(
        blood_bank_id=current_user.id
    ).all()
    
    return render_template('blood_bank/dashboard.html',
                         total_drives=total_drives,
                         upcoming_drives=upcoming_drives,
                         total_donations=total_donations,
                         all_blood_drives=all_blood_drives,
                         inventory=inventory)

@bp.route('/schedule-drive', methods=['GET', 'POST'])
@login_required
def schedule_drive():
    if current_user.user_type != 'blood_bank':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            drive = BloodDrive(
                organizer_id=current_user.id,
                title=request.form['title'],
                location=request.form['location'],
                description=request.form['description'],
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M'),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M'),
                status='scheduled'
            )
            
            db.session.add(drive)
            db.session.commit()
            
            flash('Blood drive scheduled successfully!', 'success')
            return redirect(url_for('blood_bank.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('blood_bank/schedule_drive.html')

@bp.route('/edit-drive/<int:drive_id>', methods=['GET', 'POST'])
@login_required
def edit_drive(drive_id):
    if current_user.user_type != 'blood_bank':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    drive = BloodDrive.query.get_or_404(drive_id)
    
    if drive.organizer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            drive.title = request.form['title']
            drive.location = request.form['location']
            drive.description = request.form['description']
            drive.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
            drive.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
            drive.status = request.form.get('status', 'scheduled')
            
            db.session.commit()
            flash('Blood drive updated successfully!', 'success')
            return redirect(url_for('blood_bank.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating blood drive: {str(e)}', 'error')
    
    return render_template('blood_bank/schedule_drive.html', drive=drive, is_edit=True)

@bp.route('/delete-drive/<int:drive_id>', methods=['POST'])
@login_required
def delete_drive(drive_id):
    if current_user.user_type != 'blood_bank':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    drive = BloodDrive.query.get_or_404(drive_id)
    
    if drive.organizer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    try:
        db.session.delete(drive)
        db.session.commit()
        flash('Blood drive deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting blood drive: {str(e)}', 'error')
    
    return redirect(url_for('blood_bank.dashboard'))