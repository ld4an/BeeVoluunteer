import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.messages import get_messages
from BeeVolunteer.models import User

@pytest.mark.django_db
def test_update_settings_post():
    client = Client()

    # Create user
    user = User.objects.create(
        email="old@example.com",
        first_name="Old",
        last_name="Name",
        phone="000111222",
        password=make_password("oldpass"),
        role="volunteer"
    )

    # Simulate login
    session = client.session
    session['user_id'] = user.id
    session.save()

    # Send updated form data
    response = client.post(reverse('update_settings'), data={
        'username': 'New Name',
        'email': 'new@example.com',
        'phone': '999888777',
        'password': 'newpass123'
    }, follow=True)

    # Reload user from DB
    user.refresh_from_db()

    # Check field updates
    assert user.first_name == 'New'
    assert user.last_name == 'Name'
    assert user.email == 'new@example.com'
    assert user.phone == '999888777'
    assert check_password('newpass123', user.password)

    # Check redirect success and message
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert any("updated successfully" in str(m).lower() for m in messages)
