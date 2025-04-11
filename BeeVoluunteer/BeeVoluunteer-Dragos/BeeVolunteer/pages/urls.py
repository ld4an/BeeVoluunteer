"""Defines URL patterns for pages."""
from .views import register_view, login_view, password_reset, homepage_view, account_view, logout_view,announcements_view
from django.urls import path

from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login', login_view, name='login'),
    path('reset-password', password_reset, name='password_reset'),
    path('homepage', homepage_view, name='homepage'),

    path('settings', account_view, name='settings'),
    path('my-announcements', announcements_view, name='announcements'),
    path('logout/', logout_view, name='logout'),



]
