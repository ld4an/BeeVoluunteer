import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from BeeVolunteer.models import User, Event, Organization
from django.contrib.auth.hashers import make_password
from datetime import timedelta

@pytest.mark.django_db
def test_announcements_volunteer_only_sees_own_events():
    client = Client()

    volunteer = User.objects.create(
        email="vol@example.com",
        password=make_password("pass"),
        first_name="Alice",
        last_name="Volunteer",
        phone="000",
        role="volunteer"
    )

    other = User.objects.create(
        email="someone@example.com",
        password=make_password("pass"),
        role="volunteer"
    )

    my_event = Event.objects.create(
        name="My Event",
        user=volunteer,
        date=timezone.now() + timedelta(days=1),
        is_active=True
    )

    other_event = Event.objects.create(
        name="Not My Event",
        user=other,
        date=timezone.now() + timedelta(days=2),
        is_active=True
    )

    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    response = client.get(reverse('announcements'))
    assert response.status_code == 200

    event_names = [e.name for e in response.context['events']]
    assert "My Event" in event_names
    assert "Not My Event" not in event_names


@pytest.mark.django_db
def test_announcements_organizer_only_sees_their_events():
    client = Client()

    org = Organization.objects.create(
        name="OrgName",
        email="org@example.com",
        description="Desc"
    )

    organizer = User.objects.create(
        email="org@example.com",
        password=make_password("pass"),
        role="organizer",
        organization=org
    )

    other = User.objects.create(
        email="other@example.com",
        password=make_password("pass"),
        role="organizer",
        organization=org
    )

    mine = Event.objects.create(
        name="Org Event",
        user=organizer,
        organization=org,
        date=timezone.now() + timedelta(days=1),
        is_active=True
    )

    not_mine = Event.objects.create(
        name="Other Org Event",
        user=other,
        organization=org,
        date=timezone.now() + timedelta(days=2),
        is_active=True
    )

    session = client.session
    session['user_id'] = organizer.id
    session.save()

    response = client.get(reverse('announcements'))
    assert response.status_code == 200
    names = [e.name for e in response.context['events']]
    assert "Org Event" in names
    assert "Other Org Event" not in names


@pytest.mark.django_db
def test_announcements_requires_login():
    client = Client()
    response = client.get(reverse('announcements'), follow=True)
    assert response.redirect_chain
    assert "login" in response.request["PATH_INFO"]
