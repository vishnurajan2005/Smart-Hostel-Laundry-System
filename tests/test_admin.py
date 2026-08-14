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