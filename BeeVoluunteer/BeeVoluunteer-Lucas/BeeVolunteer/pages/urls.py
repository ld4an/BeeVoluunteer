"""Defines URL patterns for pages."""
from .views import register_view, login_view, password_reset
from django.urls import path

from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login', login_view, name='login'),
    path('reset-password', password_reset, name='password_reset')
]
