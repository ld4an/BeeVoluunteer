from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

#|Ignora eroarea asta, Django e ***** si o ia din "BeeV.." cu cerc (package), nu de la radacina
from BeeVolunteer.models import User, Organization, Event, EventVolunteer
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from django.contrib.auth.hashers import check_password


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
                return redirect('two_btn')
            elif user.role == 'organizer':
                return redirect('organization_homepage')
        except User.DoesNotExist:
            pass

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')

        if check_password(password, user.password):
            request.session['user_id'] = user.id

            if remember_me:
                request.session.set_expiry(7 * 24 * 60 * 60)
            else:
                # Expiră la închiderea browserului
                request.session.set_expiry(0)

            if user.role == 'volunteer':
                return redirect('two_btn')
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
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('reset_password')

    return render(request, 'pages/reset_password.html')

@never_cache
def volunteer_homepage_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id, role='volunteer')
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    applications = EventVolunteer.objects.filter(user=user).select_related('event')
    applied_event_ids = [app.event.id for app in applications]

    events = list(Event.objects.filter(date__gte=timezone.now(), is_active=True, id__in=applied_event_ids) |
                  Event.objects.filter(date__gte=timezone.now(), is_active=True).exclude(id__in=applied_event_ids))

    app_map = {app.event.id: app for app in applications}
    for event in events:
        event.application = app_map.get(event.id)

    user_name = f"{user.first_name} {user.last_name}"
    return render(request, 'pages/homepage_volunteers.html', {
        'user_name': user_name,
        'events': events
    })
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id, role='volunteer')
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    # Obține TOATE aplicațiile acestui user
    applications = EventVolunteer.objects.filter(user=user).select_related('event')
    applied_event_ids = [app.event.id for app in applications]

    # Obține evenimentele viitoare (inclusiv cele aplicate)
    events = list(Event.objects.filter(date__gte=timezone.now(), id__in=applied_event_ids) |
                  Event.objects.filter(date__gte=timezone.now()).exclude(id__in=applied_event_ids))

    # Mapează aplicațiile după event.id
    app_map = {app.event.id: app for app in applications}

    # Injectează aplicația în fiecare event
    for event in events:
        event.application = app_map.get(event.id)

    user_name = f"{user.first_name} {user.last_name}"
    return render(request, 'pages/homepage_volunteers.html', {
        'user_name': user_name,
        'events': events
    })

@never_cache
def organization_homepage_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id, role='organizer')
        organization = user.organization
        events = Event.objects.filter(organization=organization, is_active=True)  # <- IMPORTANT
    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect('login')

    return render(request, 'pages/homepage_organization.html', {
        'organization_name': organization.name,
        'user_name': organization.name,
        'events': events
    })


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
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Session expired or user no longer exists.")
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('event_name')
        description = request.POST.get('description')
        date_str = request.POST.get('event_date')
        location = request.POST.get('location')
        max_volunteers = request.POST.get('volunteer_count')

        from datetime import datetime
        try:
            event_datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('add_event')

        if user.role == 'organizer' and user.organization:
            event_org = user.organization
        else:
            event_org, _ = Organization.objects.get_or_create(
                name="Volunteer Created Events",
                defaults={
                    'email': 'volunteers@beevent.org',
                    'description': 'Auto-assigned org for events created by volunteers',
                }
            )

        Event.objects.create(
            name=name,
            description=description,
            date=event_datetime,
            location=location,
            max_volunteers=max_volunteers,
            organization=event_org,
            user=user
        )

        return redirect('organization_homepage' if user.role == 'organizer' else 'volunteer_dashboard')

    # GET method
    user_role = user.role
    user_name = f"{user.first_name} {user.last_name}" if user_role == 'volunteer' else user.organization.name
    organization_name = user.organization.name if user_role == 'organizer' and user.organization else None

    return render(request, 'pages/add-event.html', {
        'user': user,
        'user_role': user_role,
        'user_name': user_name,
        'organization_name': organization_name
    })

@never_cache
def update_settings(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')

        if not user_id:
            messages.error(request, "You must be logged in to update your settings.")
            return redirect('login')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

        # Get data from the form
        full_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')

        # Split full name into first and last
        name_parts = full_name.strip().split(' ', 1)
        user.first_name = name_parts[0]
        user.phone=phone
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        user.email = email

        if password:
            user.password = make_password(password)

        user.save()
        messages.success(request, "Account settings updated successfully.")
        return redirect('settings')


def edit_event(request, id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    user_name = f"{user.first_name} {user.last_name}"

    # pentru organizator
    if user.role == 'organizer':
        event = get_object_or_404(Event, id=id, organization=user.organization)
    # pentru voluntar
    elif user.role == 'volunteer':
        event = get_object_or_404(Event, id=id, user=user)
    else:
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    applications = EventVolunteer.objects.filter(event=event).select_related('user')

    if request.method == 'POST':
        event.name = request.POST.get('event_name')
        event.description = request.POST.get('description')
        event.location = request.POST.get('location')
        event.max_volunteers = request.POST.get('volunteer_count')

        date_str = request.POST.get('event_date')
        from datetime import datetime
        event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        event.save()
        return redirect('organization_homepage' if user.role == 'organizer' else 'volunteer_dashboard')

    return render(request, 'pages/edit_event.html', {
        'event': event,
        'user_name': user_name,
        'applications': applications
    })


@never_cache
def delete_event(request, id):

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    # Organizator: poate șterge dacă evenimentul e al organizației
    if user.role == 'organizer':
        event = get_object_or_404(Event, id=id, organization=user.organization)
    # Voluntar: poate șterge doar propriul eveniment
    elif user.role == 'volunteer':
        event = get_object_or_404(Event, id=id, user=user)
    else:
        messages.error(request, "Unauthorized action.")
        return redirect('login')

    if request.method == 'POST':
        event.is_active = False
        event.save()
        messages.success(request, "Event deleted (marked as inactive).")

    return redirect('organization_homepage' if user.role == 'organizer' else 'volunteer_dashboard')


def apply_to_event(request, event_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to apply.")
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    event = get_object_or_404(Event, id=event_id)

    # NU permite aplicarea la evenimente inactive
    if not event.is_active:
        messages.error(request, "You cannot apply to an inactive event.")
        return redirect('volunteer_dashboard')

    application, created = EventVolunteer.objects.get_or_create(
        user=user,
        event=event,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, "You successfully applied.")
    else:
        messages.info(request, "You already applied.")

    return redirect('volunteer_dashboard')






from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from BeeVolunteer.models import Event, EventVolunteer, User

@never_cache
def volunteer_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    # Evenimente viitoare și active (dar NU cele proprii)
    events = Event.objects.filter(date__gte=timezone.now(), is_active=True).exclude(user=user)\
        .select_related('user', 'organization')

    # Aplicații
    applications = EventVolunteer.objects.filter(user=user).select_related('event')
    applied_event_ids = [app.event.id for app in applications]
    app_map = {app.event.id: app for app in applications}

    for event in events:
        event.application = app_map.get(event.id)

    # Evenimentele create de utilizator
    my_events = Event.objects.filter(user=user, is_active=True).order_by('-date')

    return render(request, 'pages/homepage_volunteers.html', {
        'user_name': f"{user.first_name} {user.last_name}",
        'user_id': user.id,  # <-- important pentru template
        'events': events,
        'my_events': my_events,
    })

@require_http_methods(["POST"])
def update_application_status(request, app_id, status):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    app = get_object_or_404(EventVolunteer, id=app_id)
    event = app.event

    if status == 'accepted':
        accepted_count = EventVolunteer.objects.filter(event=event, status='accepted').count()
        if accepted_count >= event.max_volunteers:
            messages.error(request, f"Cannot accept more than {event.max_volunteers} volunteer(s) for this event.")
            return redirect('edit_event', id=event.id)

    if status in ['accepted', 'rejected']:
        app.status = status
        app.save()
        messages.success(request, f"Application {status}.")

    return redirect('edit_event', id=event.id)

# ONE TRY
def two_btn_volunteer_page_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Session expired.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    user_name = f"{user.first_name} {user.last_name}" if user.role == 'volunteer' else user.organization.name

    # ✅ Filter events
    applied_event_ids = EventVolunteer.objects.filter(user=user).values_list('event_id', flat=True)
    now = timezone.now()
    events = Event.objects.filter(is_active=True, date__gt=now).exclude(id__in=applied_event_ids)

    return render(request, 'pages/two_btn_volunteer_homepage.html', {
        'user_name': user_name,
        'events': events,  # ✅ FIXED
    })