from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from .models import User, Profile, Purchase, Album, Song, CreateAlbumForm, UploadFileForm, UserCreationForm
import uuid
from zipfile import *
import os
from django.conf import settings
import hashlib
from utils.hints import set_user_for_sharding
from .routers import NUM_LOGICAL_SHARDS

# Create your views here.
def index(request):
    return render(request, 'web/index.html')

def scan(request):
    return render(request, 'web/scan.html')

def download(request):
    downloadKey = request.GET['dl']
    purchase_record = get_object_or_404(Purchase, _id= downloadKey)
    album_name = purchase_record.album_id.title
    if purchase_record.fulfilled:
        return HttpResponse('Sorry, looks like this download link as already expired.')
    else:
        filename = os.path.join(settings.ZIP_ROOT, purchase_record.musician_id, purchase_record.album_id._id, purchase_record.version_hash+'.zip')
        response = HttpResponse(open(filename, 'rb').read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{filename}"'.format(filename=album_name+'.zip')
        purchase_record.fulfilled = True
        purchase_record.save()
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
            musician_id = uuid.uuid4().hex[0:16]
            profile_querry = Profile.objects
            while(profile_querry.filter(musician_id=musician_id).exists()):
                musician_id = uuid.uuid4().hex[0:16]
            profile_querry.create(auth_user=new_user, musician_id=musician_id)
            pass
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
        if request.POST['age'] != '':
            profile.age = request.POST['age']
        if request.POST.__contains__('gender'):
            profile.gender = request.POST['gender']
        if request.POST.__contains__('genre'):
            profile.genre = request.POST['genre']
        profile.save()

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
    set_user_for_sharding(albums, musician_id)
    for album in albums:
        songs = Song.objects.filter(musician_id=musician_id, album_id=album._id)
        set_user_for_sharding(songs, musician_id)
        data.append({"album_id": album._id, "title": album.title, "songs": songs})

    return render(request, 'web/dashboard.html', {"data": data})

@login_required
def create_album(request):
    if request.method == "GET":
        return HttpResponseNotFound()

    musician_id = request.user.profile.musician_id
    album_id = findId(Album, 16, musician_id, False)
    form = CreateAlbumForm({'musician_id':musician_id, '_id':album_id, 'title': request.POST['title']})

    if form.is_valid():
        form.save()
        return redirect('/streeTunes/dashboard/')
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
        song_id = findId(Song, 32, musician_id, False)

        # form = UploadFileForm({
        #     'musician_id': musician_id,
        #     'album_id': request.POST['album_id'],
        #     '_id': song_id,
        #     'title': request.POST['title'],
        #     }, request.FILES)

        # if form.is_valid():
        album_query = Album.objects
        set_user_for_sharding(album_query, musician_id)
        album = album_query.get(_id=request.POST['album_id'])

        new_song = Song(
        musician_id= musician_id,
        album_id= album,
        _id= song_id,
        title= request.POST['title'],
        media= request.FILES['media']
        )
        # set_user_for_sharding(new_song, musician_id)
        new_song.save()
        return redirect('/streeTunes/dashboard/')
        # else:
        #     #Error
        #     print(form.errors)
        #     return HttpResponse('failed')
        pass
    pass



@login_required
def genqr(request):
    if request.method == 'POST':
        musician_id = request.user.profile.musician_id
        purchase_id = findId(Purchase, 16, musician.musician_id, True) + musician_id
        album = Album.objects.get(_id=request.POST['album_id'])
        set_user_for_sharding(album, musician_id)
        longitude = request.POST['longitude']
        latitude = request.POST['latitude']
        version_hash = createZip(album)
        p = Purchase(musician_id=musician_id, _id=purchase_id, album_id=album, longitude=longitude, latitude=latitude, version_hash=version_hash)
        p.save()

        return redirect('/streeTunes/qr/{pid}'.format(pid=purchase_id))
    else:
        return HttpResponseNotFound()

@login_required
def qr(request, pid):
    if(pid is None):
        return HttpResponseNotFound()
    return render(request, 'web/qr.html', {'purchase_id': pid})

def analytics(request):
    if "genre" in request.GET:
        genres = request.GET.getlist('genre')
    else:
        genres = ['jazz', 'classical', 'pop', 'blues']
    if 'weekday' in request.GET and request.GET['weekday'] != 'Any':
        weekday = [int(request.GET['weekday'])]
    else:
        weekday = [1, 2, 3, 4, 5, 6, 7]
    if 'gender' in request.GET and request.GET['gender'] != 'Any':
        gender = [request.GET['gender']]
    else:
        gender = ['Male', 'Female', None]

    all_fulfilled_purchases = []
    for shard in range(0, NUM_LOGICAL_SHARDS):
        purchases = Purchase.objects.filter(fulfilled=True, musician_id__genre__in=genres, musician_id__gender__in = gender, time__week_day__in=weekday)
        set_user_for_sharding(purchases, shard)
        all_fulfilled_purchases = all_fulfilled_purchases + [p for p in purchases]

    print(purchases)
    return render(request, 'web/analytics.html', {'purchases':all_fulfilled_purchases})

################################################################################
# Helper functions:
def createZip(album):
    songs = Song.objects.filter(album_id=album._id)
    album_id = album._id
    musician_id = album.musician_id
    musician_dir = os.path.join(settings.ZIP_ROOT, musician_id)
    if not os.path.isdir(musician_dir):
        # Create direcotry
        os.mkdir(musician_dir)
        pass
    album_dir = os.path.join(musician_dir, album_id)
    if not os.path.isdir(album_dir):
        # Create direcotry
        os.mkdir(album_dir)
        pass

    version_hash = hashlib.sha256()
    for song in songs:
        version_hash.update(bytes(song._id, encoding='utf-8'))
        pass
    filename = version_hash.hexdigest()+'.zip'
    full_filename = os.path.join(album_dir, filename)

    # If zip file already exists exit
    if(os.path.isfile(full_filename)):
        return version_hash.hexdigest()
    # else create zip
    else:
        zip_file = ZipFile(full_filename, "w")
        for song in songs:
            song_loc = os.path.join(settings.MEDIA_ROOT, str(song.media))
            zip_file.write(song_loc, song_loc.split('/')[-1])
            pass
        zip_file.close()
        return version_hash.hexdigest()

def findId(Model, length, user_id, is_purchase_id):
    _id = ''
    if is_purchase_id:
        _id = uuid.uuid4().hex[0:length] + user_id
    else:
        _id = uuid.uuid4().hex[0:length]
    model_query = Model.objects
    set_user_for_sharding(model_query, user_id)
    while(model_query.filter(_id=_id).exists()):
        _id = uuid.uuid4().hex[0:length]
        pass
    return _id
