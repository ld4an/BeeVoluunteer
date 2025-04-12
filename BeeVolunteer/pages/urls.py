"""Defines URL patterns for pages."""
from .views import register_view, login_view, password_reset, account_view, logout_view, announcements_view, \
    homepage_volunteer_view, homepage_organization_view, home, add_event
from django.urls import path

from . import views

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login', login_view, name='login'),
    path('reset-password', password_reset, name='password_reset'),

    # path('homepage', homepage_view, name='homepage'),
    path('volunteer-homepage/', homepage_volunteer_view, name='volunteer_homepage'),

    path('organization-homepage/', homepage_organization_view, name='organization_homepage'),

    path('settings', account_view, name='settings'),
    path('my-announcements', announcements_view, name='announcements'),
    path('logout/', logout_view, name='logout'),
    path('add-event/', add_event, name='add_event'),
]
