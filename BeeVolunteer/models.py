from django.db import models


# ============ Model organizatie ================
class Organization(models.Model):
    """
    Represents an organization that manages events and volunteers.
    """
    name = models.CharField(max_length=255, unique=True)
    # user = models.OneToOneField('User', on_delete=models.CASCADE, null=True, blank=True, related_name='org_profile')
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organizations"


# ======== User Model ===========
class User(models.Model):
    """
    Represents a user w

    ho can be a volunteer, admin, or event organizer.
    """
    ROLE_CHOICES = [
        ('volunteer', 'Volunteer'),  # Regular volunteer
        ('admin', 'Admin'),  # Admin with higher privileges
        ('organizer', 'Organizer'),  # Can create/manage events
    ]

    first_name = models.CharField(max_length=100, null=True, blank=True)  # User's first name
    last_name = models.CharField(max_length=100, null=True, blank=True)  # User's last name
    email = models.EmailField(unique=True)  # Unique email for authentication
    password = models.CharField(max_length=255)  # Hashed password for security
    phone = models.CharField(max_length=20, null=True, blank=True)  # Optional phone number
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='volunteer')  # Role selection
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"


# ======== Event Model ===========
class Event(models.Model):
    """
    Represents an event organized by an organization.
    """
    name = models.CharField(max_length=255)  # Name of the event
    description = models.TextField(null=True, blank=True)  # Optional description
    date = models.DateTimeField()  # Scheduled date and time
    location = models.CharField(max_length=255)  # Physical or online location
    max_volunteers = models.IntegerField(null=True, blank=True)  # Optional volunteer limit
    organization = models.ForeignKey(Organization, null=True, blank=True,
                                     on_delete=models.CASCADE)  # Event belongs to an organization
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "events"


# ======== Event Volunteer Model ===========
class EventVolunteer(models.Model):
    """
    Tracks the participation of volunteers in events.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Waiting for confirmation
        ('confirmed', 'Confirmed'),  # Approved to participate
        ('canceled', 'Canceled'),  # Canceled participation
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Volunteer participating
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # Event linked to the volunteer
    status = models.CharField(max_length=21, choices=STATUS_CHOICES, default='pending')  # Status of the participation
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the record was created

    class Meta:
        db_table = "event_volunteers"