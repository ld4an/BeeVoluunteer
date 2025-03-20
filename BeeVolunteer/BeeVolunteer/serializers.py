from rest_framework import serializers
from .models import Organization, User, Event, EventVolunteer


# ===========Converts models into JSON===============
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # Hide password in API responses


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class EventVolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVolunteer
        fields = '__all__'
