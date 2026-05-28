from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    user_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Donor specific fields
    blood_type = db.Column(db.String(5))
    last_donation_date = db.Column(db.DateTime)
    
    # Hospital specific fields
    hospital_name = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    emergency_contact = db.Column(db.String(20))
    
    # Blood Bank specific fields
    bank_name = db.Column(db.String(100))
    registration_number = db.Column(db.String(50))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Donor(User):
    __tablename__ = 'donors'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    def __repr__(self):
        return f'<Donor {self.first_name}>'


class Hospital(User):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    def __repr__(self):
        return f'<Hospital {self.hospital_name}>'


class BloodBank(User):
    __tablename__ = 'blood_banks'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    def __repr__(self):
        return f'<BloodBank {self.bank_name}>'


class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    def __repr__(self):
        return f'<Admin {self.first_name}>'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))