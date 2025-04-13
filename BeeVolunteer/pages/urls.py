"""Defines URL patterns for pages."""
from .views import register_view, login_view, password_reset, volunteer_homepage_view, account_view, announcements_view, \
    logout_view, home, add_event, homepage_organization_view
from django.urls import path

from . import views

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login', login_view, name='login'),
    path('reset-password', password_reset, name='password_reset'),
    path('volunteer_homepage', volunteer_homepage_view, name='volunteer_homepage'),
    path('organization-homepage/', homepage_organization_view, name='organization_homepage'),
    path('logout/', logout_view, name='logout'),
    path('settings/', account_view, name='settings'),
    path('my-announcements/', announcements_view, name='announcements'),
    path('add-event/', add_event, name='add_event'),
]
