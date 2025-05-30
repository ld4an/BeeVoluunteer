import pytest
from django.urls import reverse
from django.test import Client
from BeeVolunteer.models import User, Organization
from django.contrib.auth.hashers import make_password

@pytest.mark.django_db
def test_account_view_as_volunteer():
    client = Client()

    user = User.objects.create(
        email="volunteer@example.com",
        first_name="Alice",
        last_name="Smith",
        phone="0000000000",
        password=make_password("pass"),
        role="volunteer"
    )

    session = client.session
    session['user_id'] = user.id
    session.save()

    response = client.get(reverse('settings'))
    assert response.status_code == 200
    assert response.context['user_name'] == "Alice Smith"
    assert response.context['user_role'] == "volunteer"
    assert response.context['organization_name'] is None

@pytest.mark.django_db
def test_account_view_as_organizer():
    client = Client()

    org = Organization.objects.create(
        name="Save The Planet",
        email="org@example.com",
        description="Eco group"
    )

    user = User.objects.create(
        email="orguser@example.com",
        password=make_password("pass"),
        role="organizer",
        organization=org
    )

    session = client.session
    session['user_id'] = user.id
    session.save()

    response = client.get(reverse('settings'))
    assert response.status_code == 200
    assert response.context['user_role'] == "organizer"
    assert response.context['organization_name'] == "Save The Planet"
    assert response.context['user_name'] == "Save The Planet"

@pytest.mark.django_db
def test_account_view_requires_login():
    client = Client()

    response = client.get(reverse('settings'), follow=True)
    assert response.redirect_chain  # should redirect to login
    assert "login" in response.request["PATH_INFO"]
