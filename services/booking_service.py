from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from models import Booking, Machine, db

SLOTS = [
    '06:00 AM - 07:00 AM',
    '07:00 AM - 08:00 AM',
    '08:00 AM - 09:00 AM',
    '05:00 PM - 06:00 PM',
    '06:00 PM - 07:00 PM',
    '07:00 PM - 08:00 PM',
    '08:00 PM - 09:00 PM',
    '09:00 PM - 10:00 PM',
]


def validate_slot(slot):
    return slot in SLOTS


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def slot_start_datetime(booking_date, slot):
    start = slot.split(' - ')[0]
    return datetime.strptime(f'{booking_date.isoformat()} {start}', '%Y-%m-%d %I:%M %p')


def active_bookings_for_user_on_date(user_id, booking_date):
    return Booking.query.filter_by(user_id=user_id, booking_date=booking_date, status='confirmed').all()


def create_booking(user_id, machine_id, booking_date, slot):
    if booking_date < date.today():
        return None, 'Booking date cannot be in the past.', 400
    if not validate_slot(slot):
        return None, 'Please select a valid time slot.', 400

    machine = db.session.get(Machine, machine_id)
    if not machine:
        return None, 'Washing machine not found.', 404
    if machine.status != 'active':
        return None, 'This washing machine is inactive.', 400

    if booking_date == date.today() and slot_start_datetime(booking_date, slot) <= datetime.now():
        return None, 'This time slot has already started or passed.', 400

    existing_student = Booking.query.filter_by(
        user_id=user_id, booking_date=booking_date, slot=slot, status='confirmed'
    ).first()
    if existing_student:
        return None, 'You already have a booking for this time slot.', 409

    daily_count = Booking.query.filter_by(user_id=user_id, booking_date=booking_date, status='confirmed').count()
    if daily_count >= 2:
        return None, 'Maximum 2 bookings per student per day reached.', 400

    booking = Booking(user_id=user_id, machine_id=machine_id, booking_date=booking_date, slot=slot)
    db.session.add(booking)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, 'That machine and time slot is already booked.', 409
    return booking, 'Booking confirmed successfully.', 201
