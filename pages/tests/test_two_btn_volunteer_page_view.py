import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from BeeVolunteer.models import User, Event, EventVolunteer
from django.contrib.auth.hashers import make_password
from datetime import timedelta

@pytest.mark.django_db
def test_two_btn_volunteer_view_filters_correctly():
    client = Client()

    volunteer = User.objects.create(
        email="vol@example.com",
        password=make_password("pass"),
        role="volunteer",
        first_name="Test",
        last_name="User",
        phone="1234567890"
    )

    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    now = timezone.now()

    # Future + active → should be visible
    valid_event = Event.objects.create(
        name="Future Event",
        date=now + timedelta(days=3),
        location="City Hall",
        max_volunteers=10,
        description="A valid event",
        user=volunteer,
        is_active=True
    )

    # Already applied → should NOT be visible
    applied_event = Event.objects.create(
        name="Applied Event",
        date=now + timedelta(days=5),
        location="Park",
        max_volunteers=10,
        description="Already applied",
        user=volunteer,
        is_active=True
    )
    EventVolunteer.objects.create(user=volunteer, event=applied_event, status="pending")

    # Past event → should NOT be visible
    old_event = Event.objects.create(
        name="Old Event",
        date=now - timedelta(days=2),
        location="Old Place",
        max_volunteers=10,
        description="In the past",
        user=volunteer,
        is_active=True
    )

    # Inactive → should NOT be visible
    inactive_event = Event.objects.create(
        name="Inactive Event",
        date=now + timedelta(days=2),
        location="Closed Venue",
        max_volunteers=10,
        description="Not active",
        user=volunteer,
        is_active=False
    )

    response = client.get(reverse('two_btn'))
    assert response.status_code == 200

    visible = [e.name for e in response.context['events']]
    assert "Future Event" in visible
    assert "Applied Event" not in visible
    assert "Old Event" not in visible
    assert "Inactive Event" not in visible
