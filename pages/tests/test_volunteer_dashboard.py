import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from BeeVolunteer.models import User, Event, EventVolunteer
from django.contrib.auth.hashers import make_password
from datetime import timedelta

@pytest.mark.django_db
def test_volunteer_dashboard_view():
    client = Client()

    # Create volunteer
    volunteer = User.objects.create(
        email="volunteer@example.com",
        first_name="John",
        last_name="Doe",
        phone="0000000000",
        password=make_password("test123"),
        role="volunteer"
    )

    # Log in the volunteer
    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    now = timezone.now()

    # Event created by someone else
    other_user = User.objects.create(
        email="other@example.com",
        role="organizer",
        password=make_password("test123")
    )

    event_visible = Event.objects.create(
        name="Future Public Event",
        date=now + timedelta(days=5),
        location="Park",
        max_volunteers=10,
        description="Open to all",
        is_active=True,
        user=other_user
    )

    # Event created by volunteer
    event_owned = Event.objects.create(
        name="My Created Event",
        date=now + timedelta(days=3),
        location="My Place",
        max_volunteers=5,
        description="Created by me",
        is_active=True,
        user=volunteer
    )

    # Application to the public event
    EventVolunteer.objects.create(
        user=volunteer,
        event=event_visible,
        status="pending"
    )

    # Request dashboard
    response = client.get(reverse('volunteer_dashboard'))
    assert response.status_code == 200

    context_events = response.context['events']
    context_my_events = response.context['my_events']

    # Check only the external event is in 'events'
    assert any(ev.name == "Future Public Event" for ev in context_events)
    assert all(ev.user != volunteer for ev in context_events)

    # Check own event is in 'my_events'
    assert any(ev.name == "My Created Event" for ev in context_my_events)

    # Check application info is present
    for ev in context_events:
        if ev.name == "Future Public Event":
            assert hasattr(ev, 'application')
            assert ev.application.status == "pending"
