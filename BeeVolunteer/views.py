from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Organization, User, Event, EventVolunteer
from .serializers import OrganizationSerializer, UserSerializer, EventSerializer, EventVolunteerSerializer
from .serializers import UserRegisterSerializer
from rest_framework import generics


# ======== Organization API View ===========
class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows organizations to be viewed or edited.
    - Read access is allowed for everyone.
    - Write access (POST, PUT, DELETE) requires authentication.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    - Read access is public.
    - Creation and modification require authentication.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing events.
    - Public read access.
    - Creation, update, and deletion require authentication.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EventVolunteerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tracking volunteers in events.
    - Public read access.
    - Requires authentication to sign up for an event or modify records.
    """
    queryset = EventVolunteer.objects.all()
    serializer_class = EventVolunteerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    