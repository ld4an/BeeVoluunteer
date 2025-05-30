import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from BeeVolunteer.models import User, Event, Organization
from django.contrib.auth.hashers import make_password
from datetime import timedelta

@pytest.mark.django_db
def test_organizer_edits_event_successfully():
    client = Client()

    org = Organization.objects.create(
        name="TreeClub",
        email="org@example.com",
        description="Eco lovers"
    )

    organizer = User.objects.create(
        email="org@example.com",
        password=make_password("pass"),
        role="organizer",
        organization=org
    )

    event = Event.objects.create(
        name="Original Name",
        date=timezone.now() + timedelta(days=3),
        location="Old Location",
        max_volunteers=10,
        description="Old desc",
        user=organizer,
        organization=org,
        is_active=True
    )

    # Simulate login
    session = client.session
    session['user_id'] = organizer.id
    session.save()

    new_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')

    response = client.post(reverse('edit_event', args=[event.id]), data={
        'event_name': 'New Name',
        'description': 'Updated desc',
        'event_date': new_date,
        'location': 'New Location',
        'volunteer_count': '25'
    }, follow=True)

    assert response.status_code == 200
    event.refresh_from_db()
    assert event.name == 'New Name'
    assert event.description == 'Updated desc'
    assert event.location == 'New Location'
    assert event.max_volunteers == 25


@pytest.mark.django_db
def test_volunteer_edits_own_event():
    client = Client()

    volunteer = User.objects.create(
        email="vol@example.com",
        password=make_password("pass"),
        role="volunteer",
        first_name="Test",
        last_name="User",
        phone="0123456789"
    )

    event = Event.objects.create(
        name="My Event",
        date=timezone.now() + timedelta(days=2),
        location="Initial Place",
        max_volunteers=5,
        description="Something",
        user=volunteer,
        is_active=True
    )

    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    new_date = (timezone.now() + timedelta(days=4)).strftime('%Y-%m-%dT%H:%M')

    response = client.post(reverse('edit_event', args=[event.id]), data={
        'event_name': 'My Updated Event',
        'description': 'Changed description',
        'event_date': new_date,
        'location': 'Updated Place',
        'volunteer_count': '15'
    }, follow=True)

    assert response.status_code == 200
    event.refresh_from_db()
    assert event.name == 'My Updated Event'
    assert event.location == 'Updated Place'
    assert event.max_volunteers == 15
