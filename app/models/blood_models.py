from datetime import datetime
from app import db

class BloodDrive(db.Model):
    __tablename__ = 'blood_drives'
    
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organizer = db.relationship('User', foreign_keys=[organizer_id], backref='organized_drives')
    registrations = db.relationship('DriveRegistration', backref='blood_drive', lazy=True)
    
    def __repr__(self):
        return f'<BloodDrive {self.title}>'


class DriveRegistration(db.Model):
    __tablename__ = 'drive_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('blood_drives.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')
    notes = db.Column(db.Text)
    
    donor = db.relationship('User', foreign_keys=[donor_id], backref='drive_registrations')
    
    def __repr__(self):
        return f'<DriveRegistration {self.id}>'


class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    blood_type = db.Column(db.String(5), nullable=False)
    units_needed = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    patient_details = db.Column(db.Text, nullable=False)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)
    
    hospital = db.relationship('User', foreign_keys=[hospital_id], backref='hospital_requests')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requester_requests')
    # REMOVED: donations relationship from here
    
    def __repr__(self):
        return f'<BloodRequest {self.id}>'


class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.id'), nullable=True)
    blood_drive_id = db.Column(db.Integer, db.ForeignKey('blood_drives.id'), nullable=True)
    blood_type = db.Column(db.String(5), nullable=False)
    units = db.Column(db.Integer, default=1)
    donation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    donor = db.relationship('User', foreign_keys=[donor_id], backref='user_donations')
    blood_request = db.relationship('BloodRequest', foreign_keys=[request_id], backref='donations')
    
    def __repr__(self):
        return f'<Donation {self.id}>'


class BloodInventory(db.Model):
    __tablename__ = 'blood_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    blood_type = db.Column(db.String(5), nullable=False)
    units_available = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    blood_bank = db.relationship('User', foreign_keys=[blood_bank_id], backref='inventory')
    
    def __repr__(self):
        return f'<BloodInventory {self.blood_type}>'