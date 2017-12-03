from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from .models import User, Profile, Purchase, Album, Song, CreateAlbumForm, UploadFileForm, UserCreationForm
import uuid
from zipfile import *
import os
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'web/index.html')

def scan(request):
    return render(request, 'web/scan.html')

def download(request):
    downloadKey = request.GET['dl']
    purchase_record = get_object_or_404(Purchase, purchase_id= downloadKey, fulfilled = False)
    album = purchase_record.album_id
    songs = Song.objects.filter(album_id=album.album_id)

    filename = album.title+'.zip'
    zip_file = ZipFile(filename, "w")
    for song in songs:
        song_loc = os.path.join(settings.MEDIA_ROOT, str(song.media))
        zip_file.write(song_loc, song_loc.split('/')[-1])
        pass
    zip_file.close()

    response = HttpResponse(open(filename, 'rb').read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="{filename}"'.format(filename=filename)
    return response

def signup(request):
    user_form = UserCreationForm

    if request.method == "GET":
        # give signup form
        return render(request, 'web/signup.html', {'form':user_form})

    elif request.method == "POST":
        # Process Signup
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=True)
        else:
            return render(request, 'web/signup.html', {'form':user_form, 'error': 'Invalid username or password'})
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
        return redirect('/streeTunes/profile/')
    musician_id = request.user.profile.musician_id
    data = []
    albums = Album.objects.filter(musician_id=musician_id)
    for album in albums:
        songs = Song.objects.filter(musician_id=musician_id, album_id=album.album_id)
        data.append({"album_id": album.album_id, "title": album.title, "songs": songs})

    return render(request, 'web/dashboard.html', {"data": data})

@login_required
def create_album(request):
    if request.method == "GET":
        return HttpResponseNotFound()

    musician_id = request.user.profile.musician_id
    album_id = uuid.uuid4().hex[0:16]
    while(Album.objects.filter(album_id=album_id).exists()):
        album_id = uuid.uuid4().hex[0:16]
        pass
    form = CreateAlbumForm({'musician_id':musician_id, 'album_id':album_id, 'title': request.POST['title']})

    if form.is_valid():
        form.save()
        return HttpResponse('success')
    else:
        # Error
        print(form.errors)
        return HttpResponse('falied')


@login_required
def upload(request):
    if request.method == "GET":
        form = UploadFileForm()
        return render(request, 'web/upload', {'form': form})
    else:
        musician_id = request.user.profile.musician_id
        song_id = uuid.uuid4().hex
        while(Song.objects.filter(song_id=song_id).exists()):
            song_id = uuid.uuid4().hex
            pass

        form = UploadFileForm({
            'musician_id': musician_id,
            'album_id': request.POST['album_id'],
            'song_id': song_id,
            'title': request.POST['title'],
            }, request.FILES)

        if form.is_valid():
            form.save()
            return HttpResponse('success')
        else:
            #Error
            print(form.errors)
            return HttpResponse('failed')
        pass
    pass



@login_required
def genqr(request):
    if request.method == 'POST':
        musician = request.user.profile
        purchase_id = uuid.uuid4().hex
        while(Purchase.objects.filter(purchase_id=purchase_id).exists()):
            purchase_id = uuid.uuid4().hex
            pass
        album = Album.objects.get(album_id=request.POST['album_id'])
        longitude = request.POST['longitude']
        latitude = request.POST['latitude']
        try:
            p = Purchase(musician_id=musician, purchase_id=purchase_id, album_id=album, longitude=longitude, latitude=latitude)
            p.save()
        except:
            return HttpResponse('failed')

        return redirect('/streeTunes/qr/{pid}'.format(pid=purchase_id))
    else:
        return HttpResponseNotFound()


def qr(request, pid):
    if(pid is None):
        return HttpResponseNotFound()
    return HttpResponse(pid)

