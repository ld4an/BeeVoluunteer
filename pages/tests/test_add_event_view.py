import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages
from BeeVolunteer.models import User, Event, Organization
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.test import Client

@pytest.mark.django_db
def test_add_event_as_organizer():
    client = Client()

    # Create organization and organizer
    org = Organization.objects.create(
        name="Test Org",
        email="org@example.com",
        description="Test organization"
    )

    organizer = User.objects.create(
        email="organizer@example.com",
        password=make_password("securepass"),
        role="organizer",
        organization=org
    )

    # Simulate login by setting session manually
    session = client.session
    session['user_id'] = organizer.id
    session.save()

    # Prepare event data
    data = {
        'event_name': 'Beach Cleanup',
        'description': 'Clean the beach.',
        'event_date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
        'location': 'Coastline',
        'volunteer_count': '10',
    }

    # Send POST request
    response = client.post(reverse('add_event'), data, follow=True)

    # Check redirection
    assert response.status_code == 200

    # Check event created
    assert Event.objects.filter(name='Beach Cleanup', organization=org).exists()


@pytest.mark.django_db
def test_add_event_as_volunteer():
    client = Client()

    # Create volunteer user
    volunteer = User.objects.create(
        email="volunteer@example.com",
        password=make_password("securepass"),
        role="volunteer",
        first_name="Test",
        last_name="Volunteer",
        phone="0123456789"
    )

    # Simulate login
    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    # Event data
    data = {
        'event_name': 'Park Cleaning',
        'description': 'Clean the park.',
        'event_date': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
        'location': 'Central Park',
        'volunteer_count': '5',
    }

    response = client.post(reverse('add_event'), data, follow=True)
    assert response.status_code == 200

    # Event must exist and be assigned to fallback org
    event = Event.objects.get(name='Park Cleaning')
    assert event.user == volunteer
    assert event.organization.name == "Volunteer Created Events"
