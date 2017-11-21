from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate

# Create your views here.
def index(request):
    return render(request, 'web/index.html')

def scan(request):
    return HttpResponse("this is scan")

def download(request, downloadKey):
    return HttpResponse("this is download: dlkey={key}".format(key=downloadKey))

def signup(request):
    if request.method == "GET":
        return render(request, 'web/signup.html')
    else:
        # Handle signup
        return HttpResponse("You've signed up")
        pass
    pass


@login_required
def profile(request):
    return HttpResponse("this is profile")

@login_required
def dashboard(request):
    return HttpResponse("this is dashboard")

@login_required
def upload(request):
    if request.method == "GET":
        return render(request, 'web/upload')
    else:
        # Handle upload
        pass
    pass

