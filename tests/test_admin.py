def test_student_cannot_access_admin_bookings(
    student_client,
):
    response = student_client.get(
        "/api/admin/bookings"
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["success"] is False


def test_student_cannot_add_machine(
    student_client,
):
    response = student_client.post(
        "/api/admin/machines",
        json={
            "name": "Student Created Machine",
            "status": "active",
        },
    )

    assert response.status_code == 403


def test_admin_can_view_machines(admin_client):
    response = admin_client.get(
        "/api/machines"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert len(data["machines"]) == 3


def test_admin_can_add_machine(admin_client):
    response = admin_client.post(
        "/api/admin/machines",
        json={
            "name": "New Test Machine",
            "status": "active",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["machine"]["name"] == "New Test Machine"


def test_admin_can_edit_machine(admin_client):
    response = admin_client.put(
        "/api/admin/machines/1",
        json={
            "name": "Updated Test Machine",
            "status": "inactive",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["machine"]["name"] == "Updated Test Machine"
    assert data["machine"]["status"] == "inactive"


def test_admin_can_toggle_machine(admin_client):
    response = admin_client.patch(
        "/api/admin/machines/1/status",
        json={
            "status": "inactive",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["machine"]["status"] == "inactive"


def test_admin_can_filter_bookings(admin_client):
    response = admin_client.get(
        "/api/admin/bookings?status=confirmed"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert isinstance(data["bookings"], list)
from datetime import date, timedelta


def test_admin_can_filter_bookings_by_date(
    admin_client,
    student_client,
):
    booking_date = (
        date.today() + timedelta(days=7)
    ).isoformat()

    response = student_client.post(
        "/api/bookings",
        json={
            "machine_id": 1,
            "booking_date": booking_date,
            "slot": "06:00 AM - 07:00 AM",
        },
    )

    assert response.status_code == 201

    response = admin_client.get(
        f"/api/admin/bookings?date={booking_date}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert len(data["bookings"]) == 1
    assert data["bookings"][0]["booking_date"] == booking_date


def test_admin_date_filter_returns_empty_for_no_bookings(
    admin_client,
):
    booking_date = (
        date.today() + timedelta(days=100)
    ).isoformat()

    response = admin_client.get(
        f"/api/admin/bookings?date={booking_date}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["bookings"] == []


def test_admin_date_filter_rejects_invalid_date(
    admin_client,
):
    response = admin_client.get(
        "/api/admin/bookings?date=invalid-date"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "Invalid date format" in data["message"]


def test_student_cannot_use_admin_date_filter(
    student_client,
):
    response = student_client.get(
        "/api/admin/bookings?date=2026-08-14"
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["success"] is False


def test_admin_can_combine_date_and_status_filters(
    admin_client,
    student_client,
):
    booking_date = (
        date.today() + timedelta(days=8)
    ).isoformat()

    response = student_client.post(
        "/api/bookings",
        json={
            "machine_id": 1,
            "booking_date": booking_date,
            "slot": "06:00 AM - 07:00 AM",
        },
    )

    assert response.status_code == 201

    response = admin_client.get(
        "/api/admin/bookings"
        f"?date={booking_date}&status=confirmed"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert len(data["bookings"]) == 1

    booking = data["bookings"][0]

    assert booking["booking_date"] == booking_date
    assert booking["status"] == "confirmed"