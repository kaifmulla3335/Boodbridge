from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import BloodRequest, Donation, Hospital, BloodInventory
from datetime import datetime, timedelta

bp = Blueprint('hospital', __name__, url_prefix='/hospital')

@bp.route('/profile')
@login_required
def profile():
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    recent_requests = BloodRequest.query.filter_by(
        hospital_id=current_user.id
    ).order_by(BloodRequest.created_at.desc()).limit(5).all()
    
    recent_donations = Donation.query.join(BloodRequest).filter(
        BloodRequest.hospital_id == current_user.id,
        Donation.status == 'COMPLETED'
    ).order_by(Donation.donation_date.desc()).limit(5).all()
    
    return render_template('hospital/profile.html',
                         recent_requests=recent_requests,
                         recent_donations=recent_donations)

@bp.route('/blood-requests')
@login_required
def blood_requests():
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    requests = BloodRequest.query.filter_by(
        hospital_id=current_user.id
    ).order_by(BloodRequest.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('hospital/blood_requests.html', requests=requests)

@bp.route('/create-request', methods=['GET', 'POST'])
@login_required
def create_request():
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        blood_type = request.form.get('blood_type')
        units_needed = int(request.form.get('units_needed'))
        priority = request.form.get('priority')
        patient_details = request.form.get('patient_details')
        
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        
        # Check for blood availability
        blood_inventory = BloodInventory.query.filter_by(blood_type=blood_type).first()
        if not blood_inventory or blood_inventory.units_available < units_needed:
            flash(f'Requested blood group {blood_type} is not available right now or not enough units.', 'error')
            return render_template('hospital/create_request.html')

        # FIXED: Added requester_id = current_user.id
        blood_request = BloodRequest(
            hospital_id=current_user.id,
            requester_id=current_user.id,  # <-- FIX: Added this line
            blood_type=blood_type,
            units_needed=units_needed,
            priority=priority,
            patient_details=patient_details,
            deadline=deadline,
            status='PENDING'
        )
        
        db.session.add(blood_request)
        db.session.commit()
        
        flash('Blood request created successfully and is awaiting admin approval!', 'success')
        return redirect(url_for('hospital.blood_requests'))
    
    return render_template('hospital/create_request.html')

@bp.route('/request/<int:id>')
@login_required
def request_detail(id):
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    blood_request = BloodRequest.query.get_or_404(id)
    
    if blood_request.hospital_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    donations = Donation.query.filter_by(
        request_id=blood_request.id
    ).order_by(Donation.donation_date).all()
    
    return render_template('hospital/request_detail.html',
                         request=blood_request,
                         donations=donations)

@bp.route('/cancel-request/<int:id>', methods=['POST'])
@login_required
def cancel_request(id):
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    blood_request = BloodRequest.query.get_or_404(id)
    
    if blood_request.hospital_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if blood_request.status != 'PENDING':
        flash('Cannot cancel a request that is not pending', 'error')
        return redirect(url_for('hospital.request_detail', id=id))
    
    blood_request.status = 'CANCELLED'
    db.session.commit()
    
    flash('Request cancelled successfully', 'success')
    return redirect(url_for('hospital.blood_requests'))
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    pending_requests = BloodRequest.query.filter_by(
        hospital_id=current_user.id,
        status='PENDING'
    ).order_by(BloodRequest.created_at.desc()).all()

    accepted_requests = BloodRequest.query.filter_by(
        hospital_id=current_user.id,
        status='ACCEPTED'
    ).order_by(BloodRequest.created_at.desc()).all()

    rejected_requests = BloodRequest.query.filter_by(
        hospital_id=current_user.id,
        status='REJECTED'
    ).order_by(BloodRequest.created_at.desc()).all()

    fulfilled_requests = BloodRequest.query.filter_by(
        hospital_id=current_user.id,
        status='FULFILLED'
    ).order_by(BloodRequest.created_at.desc()).limit(5).all()

    return render_template('main/hospital_dashboard.html',
                           pending_requests=pending_requests,
                           accepted_requests=accepted_requests,
                           rejected_requests=rejected_requests,
                           fulfilled_requests=fulfilled_requests)
@bp.route('/update-request/<int:id>', methods=['POST'])
@login_required
def update_request(id):
    if current_user.user_type != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    blood_request = BloodRequest.query.get_or_404(id)
    
    if blood_request.hospital_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if blood_request.status != 'PENDING':
        flash('Cannot update a request that is not pending', 'error')
        return redirect(url_for('hospital.request_detail', id=id))
    
    blood_request.units_needed = int(request.form.get('units_needed'))
    blood_request.priority = request.form.get('priority')
    blood_request.patient_details = request.form.get('patient_details')
    
    deadline_str = request.form.get('deadline')
    blood_request.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    
    db.session.commit()
    
    flash('Request updated successfully', 'success')
    return redirect(url_for('hospital.request_detail', id=id))