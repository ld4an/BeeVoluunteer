from datetime import datetime

# |Ignora eroarea asta, Django e ***** si o ia din "BeeV.." cu cerc (package), nu de la radacina
from BeeVolunteer.models import User, Organization, Event
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect


# THE VERY FIRST HOMEPAGE OF THE WEBSITE...
def home(request):
    return render(request, 'pages/root-home_page.html')

def index(request):
    """The home page for BeeVolunteer."""
    return render(request, 'pages/login.html')


def login_view(request):
    if request.session.get('user_id'):
        try:
            user = User.objects.get(id=request.session['user_id'])
            if user.role == 'volunteer':
                return redirect('volunteer_homepage')
            elif user.role == 'organizer':
                return redirect('organization_homepage')
        except User.DoesNotExist:
            pass  # if user not found, allow to continue to login page

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
        if check_password(password, user.password):  # Check password against hashed one
            request.session['user_id'] = user.id
            messages.success(request, 'Logged in successfully!')
            if user.role == 'volunteer':
                return redirect('volunteer_homepage')  # Or wherever
            elif user.role == 'organizer':
                return redirect('organization_homepage')
        else:
            messages.error(request, 'Incorrect password.')
            return redirect('login')
    return render(request, 'pages/login.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role=request.POST.get('role')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')
        if role == 'volunteer':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password),
                role = role,
                phone=phone
            )
        elif role == 'organizer':
            org_name = request.POST.get('org_name')
            org_description = request.POST.get('org_description')
            org_phone = request.POST.get('org_phone')
            website = request.POST.get('website')
            organization = Organization.objects.create(
                name=org_name,
                description=org_description,
                email=email,
                phone=org_phone,
                website=website,
            )
            User.objects.create(
                email=email,
                password=make_password(password),
                role=role,
                organization=organization,
            )

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'pages/register.html')


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('reset_password')

    return render(request, 'pages/reset_password.html')


def volunteer_homepage_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id, role='volunteer')
        user_name = f"{user.first_name} {user.last_name}"
    except User.DoesNotExist:
        messages.error(request, "Invalid user or access denied.")
        return redirect('login')

    return render(request, 'pages/homepage_volunteers.html', {'user_name': user_name})

def organization_homepage_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id, role='organizer')
        organization_name = user.organization.name if user.organization else "Organization"
    except User.DoesNotExist:
        messages.error(request, "Invalid user or access denied.")
        return redirect('login')

    return render(request, 'pages/homepage_organization.html', {'organization_name': organization_name})


def account_view(request):
    return render(request, 'pages/account.html')

def announcements_view(request):
    return render(request,'pages/my_announcements.html')

def logout_view(request):
    request.session.flush()
    #messages.error(request, "Logged out successfully!")
    return redirect('login')

def add_event(request):
    if request.method == 'POST':
        name = request.POST.get('event_name')
        description = request.POST.get('description')
        date_str = request.POST.get('event_date')
        location = request.POST.get('location')
        max_volunteers = request.POST.get('volunteer_count')

        # Parse date and time
        event_datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        # Find or create a default organization for volunteer-created events
        default_org, _ = Organization.objects.get_or_create(
            name="Volunteer Created Events",
            defaults={
                'email': 'volunteers@beevent.org',
                'description': 'Auto-assigned org for events created by volunteers',
            }
        )

        # Save event
        Event.objects.create(
            name=name,
            description=description,
            date=event_datetime,
            location=location,
            max_volunteers=max_volunteers,
            organization=default_org
        )
        return redirect('volunteer_homepage')

    return render(request, 'pages/add-event.html')


# Create your views here.
