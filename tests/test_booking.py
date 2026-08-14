from datetime import date, timedelta

from models import db, Booking, User, Machine


FUTURE_DATE = (
    date.today() + timedelta(days=7)
).isoformat()


def booking_payload(
    machine_id=1,
    booking_date=None,
    slot="06:00 AM - 07:00 AM",
):
    return {
        "machine_id": machine_id,
        "booking_date": booking_date or FUTURE_DATE,
        "slot": slot,
    }


def test_student_can_create_booking(student_client):
    response = student_client.post(
        "/api/bookings",
        json=booking_payload(),
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["booking"]["status"] == "confirmed"


def test_student_can_view_own_bookings(student_client):
    response = student_client.get("/api/bookings")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert isinstance(data["bookings"], list)


def test_duplicate_machine_slot_is_rejected(
    student_client,
):
    first = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=1,
            slot="06:00 AM - 07:00 AM",
        ),
    )

    assert first.status_code == 201

    second = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=1,
            slot="06:00 AM - 07:00 AM",
        ),
    )

    assert second.status_code == 409

    data = second.get_json()

    assert data["success"] is False


def test_inactive_machine_cannot_be_booked(
    student_client,
):
    response = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=3,
            slot="06:00 AM - 07:00 AM",
        ),
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


def test_past_date_is_rejected(student_client):
    past_date = (
        date.today() - timedelta(days=1)
    ).isoformat()

    response = student_client.post(
        "/api/bookings",
        json=booking_payload(
            booking_date=past_date,
        ),
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


def test_invalid_slot_is_rejected(student_client):
    response = student_client.post(
        "/api/bookings",
        json=booking_payload(
            slot="10:00 AM - 11:00 AM",
        ),
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


def test_nonexistent_machine_is_rejected(
    student_client,
):
    response = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=9999,
        ),
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False


def test_student_cannot_have_same_time_slot_twice(
    student_client,
):
    first = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=1,
            slot="06:00 AM - 07:00 AM",
        ),
    )

    assert first.status_code == 201

    second = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=2,
            slot="06:00 AM - 07:00 AM",
        ),
    )

    assert second.status_code == 409

    data = second.get_json()

    assert data["success"] is False


def test_student_maximum_two_bookings_per_day(
    student_client,
):
    first = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=1,
            slot="06:00 AM - 07:00 AM",
        ),
    )

    assert first.status_code == 201


    second = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=2,
            slot="07:00 AM - 08:00 AM",
        ),
    )

    assert second.status_code == 201


    third = student_client.post(
        "/api/bookings",
        json=booking_payload(
            machine_id=1,
            slot="08:00 AM - 09:00 AM",
        ),
    )

    assert third.status_code == 400

    data = third.get_json()

    assert data["success"] is False


def test_student_can_cancel_own_booking(
    student_client,
):
    create_response = student_client.post(
        "/api/bookings",
        json=booking_payload(),
    )

    assert create_response.status_code == 201

    booking_id = (
        create_response
        .get_json()["booking"]["id"]
    )

    response = student_client.delete(
        f"/api/bookings/{booking_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True


def test_cancelled_booking_releases_slot(
    student_client,
):
    first = student_client.post(
        "/api/bookings",
        json=booking_payload(),
    )

    assert first.status_code == 201

    booking_id = (
        first
        .get_json()["booking"]["id"]
    )

    cancel = student_client.delete(
        f"/api/bookings/{booking_id}"
    )

    assert cancel.status_code == 200


    second = student_client.post(
        "/api/bookings",
        json=booking_payload(),
    )

    assert second.status_code == 201


def test_student_cannot_cancel_nonexistent_booking(
    student_client,
):
    response = student_client.delete(
        "/api/bookings/99999"
    )

    assert response.status_code == 404