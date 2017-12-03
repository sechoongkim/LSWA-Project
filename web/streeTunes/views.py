from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
# Create your views here.
def index(request):
    return render(request, 'web/index.html')

def scan(request):
    return HttpResponse("this is scan")

def download(request, downloadKey):
    return HttpResponse("this is download: dlkey={key}".format(key=downloadKey))

def login(request):
    return HttpResponse("this is login")

def signup(request):
    return HttpResponse("this is signup")

def profile(request):
    return HttpResponse("this is profile")

def dashboard(request):
    return HttpResponse("this is dashboard")

