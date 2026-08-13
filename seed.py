from app import app
from models import db, User, Machine

DEMO_USERS = [
    ('Demo Student', 'student@example.com', 'Student@123', 'student'),
    ('Hostel Admin', 'admin@example.com', 'Admin@123', 'admin'),
]
MACHINES = [
    ('Washing Machine 1', 'active'),
    ('Washing Machine 2', 'active'),
    ('Washing Machine 3', 'inactive'),
    ('Washing Machine 4', 'active'),
]

with app.app_context():
    db.create_all()
    for name, email, password, role in DEMO_USERS:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
    for name, status in MACHINES:
        machine = Machine.query.filter_by(name=name).first()
        if not machine:
            db.session.add(Machine(name=name, status=status))
    db.session.commit()
    print('Seed complete. Demo accounts and machines are ready.')
