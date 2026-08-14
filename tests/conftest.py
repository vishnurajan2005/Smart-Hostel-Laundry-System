import pytest

from app import app
from models import db, User, Machine


@pytest.fixture()
def test_app(tmp_path):
    database_path = tmp_path / "test_laundry.db"

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        student = User(
            name="Test Student",
            email="student@test.com",
            role="student",
        )
        student.set_password("Student@123")

        admin = User(
            name="Test Admin",
            email="admin@test.com",
            role="admin",
        )
        admin.set_password("Admin@123")

        machine1 = Machine(
            name="Test Washing Machine 1",
            status="active",
        )

        machine2 = Machine(
            name="Test Washing Machine 2",
            status="active",
        )

        inactive_machine = Machine(
            name="Inactive Washing Machine",
            status="inactive",
        )

        db.session.add_all(
            [
                student,
                admin,
                machine1,
                machine2,
                inactive_machine,
            ]
        )

        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


@pytest.fixture()
def student_client(client):
    response = client.post(
        "/api/login",
        json={
            "email": "student@test.com",
            "password": "Student@123",
        },
    )

    assert response.status_code == 200

    return client


@pytest.fixture()
def admin_client(client):
    response = client.post(
        "/api/login",
        json={
            "email": "admin@test.com",
            "password": "Admin@123",
        },
    )

    assert response.status_code == 200

    return client