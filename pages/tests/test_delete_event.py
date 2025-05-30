import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from BeeVolunteer.models import User, Event, Organization
from django.contrib.auth.hashers import make_password
from datetime import timedelta

@pytest.mark.django_db
def test_organizer_can_delete_event():
    client = Client()

    org = Organization.objects.create(
        name="GreenOrg",
        email="org@example.com",
        description="We plant trees"
    )

    organizer = User.objects.create(
        email="org@example.com",
        password=make_password("securepass"),
        role="organizer",
        organization=org
    )

    event = Event.objects.create(
        name="Plant Trees",
        date=timezone.now() + timedelta(days=2),
        location="City Park",
        max_volunteers=20,
        description="Environmental event",
        user=organizer,
        organization=org,
        is_active=True
    )

    # Simulate login
    session = client.session
    session['user_id'] = organizer.id
    session.save()

    response = client.post(reverse('delete_event', args=[event.id]), follow=True)
    assert response.status_code == 200

    # Refresh and check is_active is now False
    event.refresh_from_db()
    assert event.is_active is False


@pytest.mark.django_db
def test_volunteer_can_delete_own_event():
    client = Client()

    volunteer = User.objects.create(
        email="vol@example.com",
        password=make_password("securepass"),
        role="volunteer",
        first_name="Test",
        last_name="User",
        phone="0000000000"
    )

    event = Event.objects.create(
        name="Cleanup Drive",
        date=timezone.now() + timedelta(days=1),
        location="Riverbank",
        max_volunteers=5,
        description="Volunteer event",
        user=volunteer,
        is_active=True
    )

    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    response = client.post(reverse('delete_event', args=[event.id]), follow=True)
    assert response.status_code == 200

    event.refresh_from_db()
    assert event.is_active is False
