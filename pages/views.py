from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
#|Ignora eroarea asta, Django e ***** si o ia din "BeeV.." cu cerc (package), nu de la radacina
from BeeVolunteer.models import User, Organization, Event
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache
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
           # messages.success(request, 'Logged in successfully!')
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

@never_cache
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

@never_cache
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



@never_cache
def account_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        user = User.objects.select_related('organization').get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user or access denied.")
        return redirect('login')

    user_role = user.role
    user_name = f"{user.first_name} {user.last_name}" if user_role == 'volunteer' else user.organization.name
    organization_name = user.organization.name if user_role == 'organizer' and user.organization else None

    return render(request, 'pages/account.html', {
        'user': user,
        'user_role': user_role,
        'user_name': user_name,
        'organization_name': organization_name
    })

@never_cache
def announcements_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        user = User.objects.select_related('organization').get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect('login')

    # Afișează DOAR evenimentele create de acest utilizator (nu după organizație!)
    events = Event.objects.filter(user_id=user.id).order_by('-date')

    # Nume pentru navbar
    user_name = f"{user.first_name} {user.last_name}" if user.role == 'volunteer' else user.organization.name

    return render(request, 'pages/my_announcements.html', {
        'events': events,
        'user_name': user_name
    })

def logout_view(request):
    request.session.flush()
    #messages.error(request, "Logged out successfully!")
    return redirect('login')

@never_cache
def add_event(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user or access denied.")
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('event_name')
        description = request.POST.get('description')
        date_str = request.POST.get('event_date')
        location = request.POST.get('location')
        max_volunteers = request.POST.get('volunteer_count')

        # Parsează data
        try:
            event_datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('add_event')

        # Creează evenimentul fără organizație, doar cu user-ul creator
        Event.objects.create(
            name=name,
            description=description,
            date=event_datetime,
            location=location,
            max_volunteers=max_volunteers,
            user=user,
            organization=None  # <- forțăm să fie mereu None
        )

        # Redirect în funcție de rol
        redirect_target = 'organization_homepage' if user.role == 'organizer' else 'volunteer_homepage'
        messages.success(request, "Event created successfully.")
        return redirect(redirect_target)

    # Context pentru navbar
    user_role = user.role
    user_name = f"{user.first_name} {user.last_name}" if user_role == 'volunteer' else user.organization.name
    organization_name = user.organization.name if user_role == 'organizer' and user.organization else None

    return render(request, 'pages/add-event.html', {
        'user': user,
        'user_role': user_role,
        'user_name': user_name,
        'organization_name': organization_name
    })
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect
from BeeVolunteer.models import User, Organization

from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect, render
from BeeVolunteer.models import User

@never_cache
def update_settings(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        user = User.objects.select_related('organization').get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user or access denied.")
        return redirect('login')

    error_password_mismatch = False

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        user.email = email

        if password:
            if password != confirm_password:
                error_password_mismatch = True
            else:
                user.password = make_password(password)

        if user.role == 'volunteer':
            full_name = request.POST.get('username', '')
            phone = request.POST.get('phone', '')
            name_parts = full_name.strip().split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.phone = phone

        elif user.role == 'organizer' and user.organization:
            org = user.organization
            org.name = request.POST.get('org_name', org.name)
            org.description = request.POST.get('org_description', org.description)
            org.phone = request.POST.get('org_phone', org.phone)
            org.website = request.POST.get('website', org.website)
            org.save()

        if not error_password_mismatch:
            user.save()
            messages.success(request, "Account settings updated successfully.")

    user_role = user.role
    user_name = f"{user.first_name} {user.last_name}" if user_role == 'volunteer' else user.organization.name
    organization_name = user.organization.name if user_role == 'organizer' and user.organization else None

    return render(request, 'pages/account.html', {
        'user': user,
        'user_role': user_role,
        'user_name': user_name,
        'organization_name': organization_name,
        'error_password_mismatch': error_password_mismatch
    })

# Create your views here.
