from app import create_app, db
from app.models import User, BloodDrive, BloodInventory, BloodRequest
from datetime import datetime, timedelta

def setup_database():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Tables created...")
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@gmail.com').first()
        if not admin:
            admin = User(
                email='admin@gmail.com',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                is_active=True
            )
            admin.set_password('admin@123')
            db.session.add(admin)
            print("✅ Admin created...")
        
        # Check if blood bank exists
        blood_bank = User.query.filter_by(email='bloodbank@example.com').first()
        if not blood_bank:
            blood_bank = User(
                email='bloodbank@example.com',
                first_name='City',
                last_name='Blood Bank',
                user_type='blood_bank',
                is_active=True,
                bank_name='City Blood Bank'
            )
            blood_bank.set_password('bank123')
            db.session.add(blood_bank)
            print("✅ Blood bank created...")
        
        # Check if hospital exists
        hospital = User.query.filter_by(email='hospital@example.com').first()
        if not hospital:
            hospital = User(
                email='hospital@example.com',
                first_name='City',
                last_name='Hospital',
                user_type='hospital',
                is_active=True,
                hospital_name='City General Hospital'
            )
            hospital.set_password('hospital123')
            db.session.add(hospital)
            print("✅ Hospital created...")
        
        # Check if donor exists
        donor = User.query.filter_by(email='donor@example.com').first()
        if not donor:
            donor = User(
                email='donor@example.com',
                first_name='John',
                last_name='Doe',
                user_type='donor',
                is_active=True,
                blood_type='O+'
            )
            donor.set_password('donor123')
            db.session.add(donor)
            print("✅ Donor created...")
        
        db.session.commit()
        
        # Get IDs after commit
        blood_bank = User.query.filter_by(email='bloodbank@example.com').first()
        hospital = User.query.filter_by(email='hospital@example.com').first()
        
        # Create blood drives
        drives = BloodDrive.query.all()
        if len(drives) == 0:
            drive1 = BloodDrive(
                organizer_id=blood_bank.id,
                title='Community Blood Drive',
                location='City Community Center',
                description='Join us for our monthly community blood drive',
                start_date=datetime.now() + timedelta(days=7),
                end_date=datetime.now() + timedelta(days=7, hours=8),
                target_donors=50,
                blood_types_needed='A+,B+,O+',
                status='scheduled'
            )
            drive2 = BloodDrive(
                organizer_id=blood_bank.id,
                title='Emergency Blood Collection',
                location='City Hospital',
                description='Urgent blood collection',
                start_date=datetime.now() + timedelta(days=3),
                end_date=datetime.now() + timedelta(days=3, hours=6),
                target_donors=30,
                blood_types_needed='O-,A-',
                status='scheduled'
            )
            db.session.add_all([drive1, drive2])
            db.session.commit()
            print("✅ Blood drives created...")
        
        # Create inventory
        inventory = BloodInventory.query.all()
        if len(inventory) == 0:
            blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            for bt in blood_types:
                inv = BloodInventory(
                    blood_type=bt,
                    units_available=50 if bt in ['O+', 'A+', 'B+'] else 20
                )
                db.session.add(inv)
            db.session.commit()
            print("✅ Inventory created...")
        
        # Create blood requests
        requests = BloodRequest.query.all()
        if len(requests) == 0:
            req1 = BloodRequest(
                hospital_id=hospital.id,
                requester_id=hospital.id,
                blood_type='O-',
                units_needed=5,
                priority='CRITICAL',
                patient_details='Emergency surgery patient',
                deadline=datetime.now() + timedelta(hours=24),
                status='PENDING'
            )
            req2 = BloodRequest(
                hospital_id=hospital.id,
                requester_id=hospital.id,
                blood_type='A+',
                units_needed=3,
                priority='HIGH',
                patient_details='Trauma patient',
                deadline=datetime.now() + timedelta(hours=48),
                status='PENDING'
            )
            db.session.add_all([req1, req2])
            db.session.commit()
            print("✅ Blood requests created...")
        
        print("\n" + "="*50)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\n📋 LOGIN CREDENTIALS:")
        print("-"*40)
        print("  👑 Admin:      admin@gmail.com / admin@123")
        print("  🩸 Blood Bank: bloodbank@example.com / bank123")
        print("  🏥 Hospital:   hospital@example.com / hospital123")
        print("  ❤️ Donor:      donor@example.com / donor123")
        print("-"*40)
        print("="*50)

if __name__ == '__main__':
    setup_database()