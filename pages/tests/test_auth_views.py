import pytest
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from BeeVolunteer.models import User


@pytest.mark.django_db
def test_register_view_success():
    client = Client()
    response = client.post(reverse('register'), data={
        'email': 'testuser@example.com',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'volunteer',
        'first_name': 'Test',
        'last_name': 'User',
        'phone': '1234567890'
    }, follow=True)

    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert any("Account created successfully!" in str(m) for m in messages)
    assert User.objects.filter(email='testuser@example.com').exists()

@pytest.mark.django_db
def test_register_password_mismatch():
    client = Client()
    response = client.post(reverse('register'), data={
        'email': 'mismatch@example.com',
        'password': 'pass123',
        'confirm_password': 'wrongpass',
        'role': 'volunteer',
        'first_name': 'Test',
        'last_name': 'Mismatch',
        'phone': '1234567890'
    }, follow=True)

    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert any("Passwords do not match." in str(m) for m in messages)
    assert not User.objects.filter(email='mismatch@example.com').exists()

from django.contrib.auth.hashers import make_password

@pytest.mark.django_db
def test_login_view_success():
    client = Client()
    user = User.objects.create(
        email='login@example.com',
        password=make_password('testpass123'),
        role='volunteer',
        first_name='Login',
        last_name='Test',
        phone='0000000000'
    )

    response = client.post(reverse('login'), data={
        'email': 'login@example.com',
        'password': 'testpass123'
    }, follow=True)

    assert response.status_code == 200
    assert client.session.get('user_id') == user.id

@pytest.mark.django_db
def test_login_view_wrong_password():
    client = Client()
    user = User.objects.create(
        email='wrongpass@example.com',
        role='volunteer',
        password=make_password('correctpass')
    )

    response = client.post(reverse('login'), data={
        'email': 'wrongpass@example.com',
        'password': 'incorrectpass'
    }, follow=True)

    messages = list(get_messages(response.wsgi_request))
    assert any("Incorrect password." in str(m) for m in messages)
    assert 'user_id' not in client.session

