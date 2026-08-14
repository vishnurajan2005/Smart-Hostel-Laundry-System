def test_student_login_success(client):
    response = client.post(
        "/api/login",
        json={
            "email": "student@test.com",
            "password": "Student@123",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["user"]["role"] == "student"


def test_login_invalid_password(client):
    response = client.post(
        "/api/login",
        json={
            "email": "student@test.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["success"] is False


def test_unauthenticated_api_requires_login(client):
    response = client.get("/api/me")

    assert response.status_code == 401

    data = response.get_json()

    assert data["success"] is False


def test_student_can_access_me(student_client):
    response = student_client.get("/api/me")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["user"]["role"] == "student"


def test_logout(student_client):
    response = student_client.post("/api/logout")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True

    response = student_client.get("/api/me")

    assert response.status_code == 401