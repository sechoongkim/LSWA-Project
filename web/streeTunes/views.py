from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from .models import *

# Create your views here.
def index(request):
    return render(request, 'web/index.html')

def scan(request):
    return render(request, 'web/scan.html')

def download(request, downloadKey):
    return HttpResponse("this is download: dlkey={key}".format(key=downloadKey))

def signup(request):
    if request.method == "GET":
        # give signup form
        user_form = UserCreationForm
        return render(request, 'web/signup.html', {'form':user_form})

    elif request.method == "POST":
        # Process Signup
        form = UserCreationForm(request.POST)
        new_user = form.save()
        # Log in that user.
        user = authenticate(username=new_user.username,
                            password=form.clean_password2())
        if user is not None:
          login(request, user)
        else:
          raise Exception

        # Take them to Profile
        request.session['first_login'] = True
        return redirect('/streeTunes/dashboard/')
        pass
    else:
        return HttpResponseNotFound()
    pass


@login_required
def profile(request):
    profile = request.user.profile
    musician_id = profile.musician_id
    gender = profile.gender
    genre = profile.genre
    age = profile.age

    if request.method == "POST":
        # TODO: UPDATE PROFILE FOR LOGGED IN USER
        cur_user = request.user

        if request.POST['age'] != '':
            cur_user.profile.age = request.POST['age']
        if request.POST.__contains__('gender'):
            cur_user.profile.gender = request.POST['gender']
        if request.POST.__contains__('genre'):
            cur_user.profile.genre = request.POST['genre']

        cur_user.save()
        return redirect('/streeTunes/profile/')

    return render(request, 'web/profile.html', {'username': request.user.username, 'profile': {'gender': gender, 'genre':genre, 'age': age}})

@login_required
def dashboard(request):
    # Check if this is a first login (ie. just after signup)
    if request.session.has_key('first_login'):
        request.session.pop('first_login')
        return redirect('/streeTunes/profile')

    return render(request, 'web/dashboard.html')

@login_required
def upload(request):
    if request.method == "GET":
        return render(request, 'web/upload')
    else:
        # Handle upload
        pass
    pass

