import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from django.contrib.messages import get_messages
from BeeVolunteer.models import User, Event, EventVolunteer
from django.contrib.auth.hashers import make_password
from datetime import timedelta

@pytest.mark.django_db
def test_apply_to_event_success():
    client = Client()

    # Create a volunteer user
    volunteer = User.objects.create(
        email="volunteer@example.com",
        password=make_password("securepass"),
        role="volunteer",
        first_name="Test",
        last_name="Volunteer",
        phone="0123456789"
    )

    # Create an active future event
    event = Event.objects.create(
        name="Test Event",
        description="A test event",
        date=timezone.now() + timedelta(days=5),
        location="Test Location",
        max_volunteers=10,
        is_active=True,
        user=volunteer  # creator
    )

    # Log in the volunteer
    session = client.session
    session['user_id'] = volunteer.id
    session.save()

    # First apply
    url = reverse('apply_to_event', args=[event.id])
    response = client.get(url, follow=True)
    assert response.status_code == 200

    # Check that application was created
    application = EventVolunteer.objects.filter(user=volunteer, event=event).first()
    assert application is not None
    assert application.status == "pending"

    # Get messages from response
    messages = list(get_messages(response.wsgi_request))
    assert any("successfully applied" in str(m).lower() for m in messages)

    # Second apply (should not create duplicate)
    response2 = client.get(url, follow=True)
    assert response2.status_code == 200

    messages2 = list(get_messages(response2.wsgi_request))
    assert any("already applied" in str(m).lower() for m in messages2)

    # Still only one application
    assert EventVolunteer.objects.filter(user=volunteer, event=event).count() == 1
