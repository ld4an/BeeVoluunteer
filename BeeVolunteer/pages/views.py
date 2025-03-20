from django.shortcuts import render


def index(request):
    """The home page for BeeVolunteer."""
    return render(request, 'pages/index.html')
# Create your views here.
