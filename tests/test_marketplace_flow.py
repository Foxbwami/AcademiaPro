from datetime import datetime, timedelta
import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app import mail
from app.extensions import db
from app.models import Message, Order, User


@pytest.fixture()
def app(monkeypatch):
    fd, test_db_path = tempfile.mkstemp(prefix="academicpro_test_", suffix=".db")
    os.close(fd)
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", f"sqlite:///{test_db_path}")
    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        MAIL_SUPPRESS_SEND=True,
    )
    monkeypatch.setattr(mail, "send", lambda _msg: None)
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass


@pytest.fixture()
def client(app):
    return app.test_client()


def _create_user(email, name, password, role="client"):
    user = User(
        email=email,
        name=name,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def _admin_login(client, email, password):
    return client.post(
        "/staff-portal",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def _logout(client):
    return client.get("/logout", follow_redirects=True)


def test_student_order_admin_status_flow(app, client):
    with app.app_context():
        client_user = _create_user("client@example.com", "Client User", "pass12345")
        _create_user("bwamistevenez001@gmail.com", "Admin User", "pass12345", role="admin")
        client_id = client_user.id

    _login(client, "client@example.com", "pass12345")
    deadline = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")
    response = client.post(
        "/order",
        data={
            "name": "Client User",
            "email": "client@example.com",
            "subject": "History Essay",
            "service_track": "writing",
            "task_type": "Essay",
            "word_count": "1500",
            "level": "Undergrad",
            "citation_style": "APA",
            "sources_count": "4",
            "currency": "USD",
            "timezone": "Africa/Nairobi",
            "details": "Need a 1500-word essay.",
            "deadline": deadline,
            "accept_terms": "y",
            "accept_privacy": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    _logout(client)

    with app.app_context():
        order = Order.query.filter_by(user_id=client_id).first()
        assert order is not None
        assert order.status == "Pending Review"
        order_id = order.id

    _admin_login(client, "bwamistevenez001@gmail.com", "pass12345")
    response = client.post(
        f"/admin/order/{order_id}/update",
        data={"status": "In Progress"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    _logout(client)

    with app.app_context():
        updated_order = db.session.get(Order, order_id)
        assert updated_order.status == "In Progress"


def test_order_chat_is_client_and_admin_only(app, client):
    with app.app_context():
        client_user = _create_user("client2@example.com", "Client Two", "pass12345")
        outsider_user = _create_user("outsider@example.com", "Outsider", "pass12345")
        admin_user = _create_user("bwamistevenez001@gmail.com", "Admin User", "pass12345", role="admin")

        order = Order(
            topic="Business Case Study",
            description="Write a case analysis.",
            deadline=datetime.utcnow() + timedelta(days=3),
            word_count=1200,
            level="Undergrad",
            status="In Progress",
            user_id=client_user.id,
        )
        db.session.add(order)
        db.session.commit()
        order_id = order.id
        admin_id = admin_user.id
        outsider_email = outsider_user.email

    _login(client, outsider_email, "pass12345")
    outsider_resp = client.get(f"/orders/{order_id}/chat")
    _logout(client)
    assert outsider_resp.status_code == 403

    _login(client, "client2@example.com", "pass12345")
    client_get = client.get(f"/orders/{order_id}/chat")
    assert client_get.status_code == 200
    client.post(
        f"/orders/{order_id}/chat",
        data={"message": "Hello admin, please follow APA."},
        follow_redirects=True,
    )
    _logout(client)

    _admin_login(client, "bwamistevenez001@gmail.com", "pass12345")
    admin_get = client.get(f"/orders/{order_id}/chat")
    _logout(client)
    assert admin_get.status_code == 200

    with app.app_context():
        sent = Message.query.filter(
            Message.content.like(f"[Order #{order_id}]%"),
            Message.receiver_id == admin_id,
        ).all()
        assert len(sent) >= 1
