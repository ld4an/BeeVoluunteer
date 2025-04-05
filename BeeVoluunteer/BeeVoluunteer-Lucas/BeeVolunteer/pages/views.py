from django.shortcuts import render, redirect
from django.contrib import messages
#|Ignora eroarea asta, Django e ***** si o ia din "BeeV.." cu cerc (package), nu de la radacina
#v
from BeeVolunteer.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


def index(request):
    """The home page for BeeVolunteer."""
    return render(request, 'pages/login.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return redirect('login')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')

        if check_password(password, user.password):
            # Salvăm user-ul în sesiune
            request.session['user_id'] = user.id

            # Redirect spre homepage
            messages.success(request, 'Logged in successfully!')
            return redirect('homepage')
        else:
            messages.error(request, 'Incorrect password.')
            return redirect('login')

    return render(request, 'pages/login.html')



def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
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

def homepage_view(request):
    user_id = request.session.get('user_id')
    user_name = "Utilizator"

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_name = f"{user.first_name} {user.last_name}"
        except User.DoesNotExist:
            pass

    return render(request, 'pages/homepage.html', {'user_name': user_name})


def account_view(request):
    return render(request, 'pages/account.html')

def announcements_view(request):
    return render(request,'pages/my_announcements.html')



def logout_view(request):
    request.session.flush()
    #messages.error(request, "Logged out successfully!")
    return redirect('login')


# Create your views here.
