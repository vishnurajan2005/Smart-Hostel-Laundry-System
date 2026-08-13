from datetime import date, datetime
from functools import wraps
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from config import Config
from models import db, User, Machine, Booking
from services.booking_service import SLOTS, parse_date, create_booking, slot_start_datetime

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def json_error(message, status=400):
    return jsonify({'success': False, 'message': message}), status


def current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user():
            if request.path.startswith('/api/'):
                return json_error('Authentication required.', 401)
            return redirect(url_for('login_page'))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            if request.path.startswith('/api/'):
                return json_error('Authentication required.', 401)
            return redirect(url_for('login_page'))
        if user.role != 'admin':
            if request.path.startswith('/api/'):
                return json_error('Admin access required.', 403)
            return redirect(url_for('dashboard_page'))
        return view(*args, **kwargs)
    return wrapper


def serialize_user(user):
    return {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}


def serialize_machine(machine):
    return {'id': machine.id, 'name': machine.name, 'status': machine.status}


def serialize_booking(booking):
    return {
        'id': booking.id,
        'user_id': booking.user_id,
        'student_name': booking.user.name if booking.user else None,
        'student_email': booking.user.email if booking.user else None,
        'machine_id': booking.machine_id,
        'machine_name': booking.machine.name if booking.machine else None,
        'booking_date': booking.booking_date.isoformat(),
        'slot': booking.slot,
        'status': booking.status,
        'created_at': booking.created_at.isoformat() if booking.created_at else None,
        'cancelled_at': booking.cancelled_at.isoformat() if booking.cancelled_at else None,
    }


@app.context_processor
def inject_globals():
    return {'current_user': current_user(), 'today': date.today().isoformat(), 'slots': SLOTS}


@app.get('/')
def index():
    user = current_user()
    if not user:
        return redirect(url_for('login_page'))
    return redirect(url_for('admin_page' if user.role == 'admin' else 'dashboard_page'))


@app.get('/login')
def login_page():
    return render_template('login.html')


@app.get('/register')
def register_page():
    return render_template('register.html')


@app.get('/dashboard')
@login_required
def dashboard_page():
    if current_user().role == 'admin':
        return redirect(url_for('admin_page'))
    return render_template('dashboard.html')


@app.get('/book')
@login_required
def booking_page():
    if current_user().role == 'admin':
        return redirect(url_for('admin_page'))
    return render_template('booking.html')


@app.get('/admin')
@admin_required
def admin_page():
    return render_template('admin.html')


@app.post('/api/register')
def api_register():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    if len(name) < 2:
        return json_error('Name must contain at least 2 characters.')
    if '@' not in email or '.' not in email.split('@')[-1]:
        return json_error('Enter a valid email address.')
    if len(password) < 8:
        return json_error('Password must contain at least 8 characters.')
    if User.query.filter_by(email=email).first():
        return json_error('An account with this email already exists.', 409)
    user = User(name=name, email=email, role='student')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Registration successful.', 'user': serialize_user(user)}), 201


@app.post('/api/login')
def api_login():
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return json_error('Invalid email or password.', 401)
    session.clear()
    session['user_id'] = user.id
    session['role'] = user.role
    return jsonify({'success': True, 'message': 'Login successful.', 'user': serialize_user(user)})


@app.post('/api/logout')
@login_required
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})


@app.get('/api/me')
@login_required
def api_me():
    return jsonify({'success': True, 'user': serialize_user(current_user())})


@app.get('/api/machines')
@login_required
def api_machines():
    machines = Machine.query.order_by(Machine.id).all()
    return jsonify({'success': True, 'machines': [serialize_machine(m) for m in machines]})


@app.get('/api/slots')
@login_required
def api_slots():
    return jsonify({'success': True, 'slots': SLOTS})


@app.post('/api/bookings')
@login_required
def api_create_booking():
    user = current_user()
    if user.role != 'student':
        return json_error('Students only.', 403)
    data = request.get_json(silent=True) or {}
    machine_id = data.get('machine_id')
    booking_date = parse_date(data.get('booking_date'))
    slot = data.get('slot')
    try:
        machine_id = int(machine_id)
    except (TypeError, ValueError):
        return json_error('A valid machine is required.')
    if not booking_date:
        return json_error('Enter a valid booking date.')
    booking, message, status = create_booking(user.id, machine_id, booking_date, slot)
    if not booking:
        return json_error(message, status)
    return jsonify({'success': True, 'message': message, 'booking': serialize_booking(booking)}), status


@app.get('/api/bookings')
@login_required
def api_bookings():
    user = current_user()
    if user.role != 'student':
        return json_error('Students only.', 403)
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.booking_date.desc(), Booking.id.desc()).all()
    return jsonify({'success': True, 'bookings': [serialize_booking(b) for b in bookings]})


@app.delete('/api/bookings/<int:booking_id>')
@login_required
def api_cancel_booking(booking_id):
    user = current_user()
    booking = db.session.get(Booking, booking_id)
    if user.role != 'student':
        return json_error('Students only.', 403)
    if not booking:
        return json_error('Booking not found.', 404)
    if booking.user_id != user.id:
        return json_error('You can only cancel your own bookings.', 403)
    if booking.status != 'confirmed':
        return json_error('This booking is already cancelled.', 400)
    if slot_start_datetime(booking.booking_date, booking.slot) <= datetime.now():
        return json_error('Cancellation is not allowed after the booking start time.', 400)
    booking.status = 'cancelled'
    booking.cancelled_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking cancelled and slot released.'})


@app.get('/api/admin/bookings')
@admin_required
def api_admin_bookings():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    query = Booking.query.join(User).join(Machine)
    if search:
        term = f'%{search}%'
        query = query.filter(or_(User.name.ilike(term), User.email.ilike(term), Machine.name.ilike(term), Booking.slot.ilike(term)))
    if status in {'confirmed', 'cancelled'}:
        query = query.filter(Booking.status == status)
    bookings = query.order_by(Booking.booking_date.desc(), Booking.id.desc()).all()
    return jsonify({'success': True, 'bookings': [serialize_booking(b) for b in bookings]})


@app.post('/api/admin/machines')
@admin_required
def api_admin_add_machine():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    status = data.get('status', 'active')
    if len(name) < 2:
        return json_error('Machine name is required.')
    if status not in {'active', 'inactive'}:
        return json_error('Invalid machine status.')
    if Machine.query.filter_by(name=name).first():
        return json_error('A machine with this name already exists.', 409)
    machine = Machine(name=name, status=status)
    db.session.add(machine)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Machine added.', 'machine': serialize_machine(machine)}), 201


@app.put('/api/admin/machines/<int:machine_id>')
@admin_required
def api_admin_edit_machine(machine_id):
    machine = db.session.get(Machine, machine_id)
    if not machine:
        return json_error('Machine not found.', 404)
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', machine.name)).strip()
    status = data.get('status', machine.status)
    if len(name) < 2:
        return json_error('Machine name is required.')
    if status not in {'active', 'inactive'}:
        return json_error('Invalid machine status.')
    duplicate = Machine.query.filter(Machine.name == name, Machine.id != machine.id).first()
    if duplicate:
        return json_error('A machine with this name already exists.', 409)
    machine.name, machine.status = name, status
    db.session.commit()
    return jsonify({'success': True, 'message': 'Machine updated.', 'machine': serialize_machine(machine)})


@app.delete('/api/admin/machines/<int:machine_id>')
@admin_required
def api_admin_delete_machine(machine_id):
    machine = db.session.get(Machine, machine_id)
    if not machine:
        return json_error('Machine not found.', 404)
    if Booking.query.filter_by(machine_id=machine.id, status='confirmed').first():
        return json_error('Cannot delete a machine with active bookings.', 409)
    db.session.delete(machine)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Machine deleted.'})


@app.patch('/api/admin/machines/<int:machine_id>/status')
@admin_required
def api_admin_toggle_machine(machine_id):
    machine = db.session.get(Machine, machine_id)
    if not machine:
        return json_error('Machine not found.', 404)
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in {'active', 'inactive'}:
        return json_error('Status must be active or inactive.')
    machine.status = status
    db.session.commit()
    return jsonify({'success': True, 'message': 'Machine status updated.', 'machine': serialize_machine(machine)})


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return json_error('Resource not found.', 404)
    return render_template('error.html', code=404, message='The page you requested was not found.'), 404


@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return json_error('An unexpected server error occurred.', 500)
    return render_template('error.html', code=500, message='Something went wrong. Please try again.'), 500


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
