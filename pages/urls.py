"""Defines URL patterns for pages."""
from .views import register_view, home,login_view, password_reset, volunteer_homepage_view, account_view, announcements_view, \
    logout_view, add_event, organization_homepage_view
from django.urls import path

from . import views

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login', login_view, name='login'),
    path('reset-password', password_reset, name='password_reset'),
    path('volunteer_homepage', volunteer_homepage_view, name='volunteer_homepage'),
    path('organization-homepage/', organization_homepage_view, name='organization_homepage'),
    path('logout/', logout_view, name='logout'),
    path('settings/', account_view, name='settings'),
    path('settings/update/', views.update_settings, name='update_settings'),
    path('my-announcements/', announcements_view, name='announcements'),
    path('add-event/', add_event, name='add_event'),
]
