from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Profile(models.Model):
    """
        Profile model auguments User model
        * musician_id is a unique 16 character key (converted from a 16 digit hex ie.64 bit)
            musician_id will serve as the sharding key across all models except User
        * auth_user points to an entry in the User model, which is used for authentication
    """
    musician_id = models.CharField(primary_key=True, max_length=16, default=uuid.uuid4().hex[0:16], editable=False)
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, null=True, default=None)
    age = models.IntegerField(null=True, default=None)
    genre = models.CharField(max_length=10, null=True, default=None)
    pass

#########################################################
# This block of code was taken from:
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html

# Automaticaly create a Profile for every user created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(auth_user=instance)
        pass
    pass

# Automaticaly save Profile when user saves
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    pass

#######################################################

class Purchase(models.Model):
    """
        Purchase model represents a potential download.
            An entry is created on every QR code generation.
        * purchase_id is a 32 character key. The first 16 is the album_id this purchase points to
        * musician_id is a ForeignKey pointing to a musician Profile
        * longitude and latitude stores information about where the purchase was generated
            (location of end user)
        * time stores information about when the purchase was generated
        * fulfilled shows if a purchase was completed (ie. end user downloaded the album)
    """
    purchase_id = models.CharField(max_length=32, primary_key=True, editable=False)
    musician_id = models.ForeignKey(Profile)
    time = models.DateTimeField()
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    fulfilled = models.BooleanField(default=False)
    pass

class Album(models.Model):
    """
        Album model represents a user defined collection of songs
        * album_id is a 16 character key with no semantics
        * musician_id is a ForeignKey pointing to a musician Profile (owner of album)
    """
    album_id = models.CharField(max_length=16, primary_key=True, editable=False)
    musician_id = models.ForeignKey(Profile)


def user_directory_path(instance, filename):
    """
        file will be uploaded to MEDIA_ROOT/<musician_id>/<album_id>/<filename>
    """
    return '{0}/{1}/{2}'.format(instance.musician_id, instance.song_id[0:16], filename)
class Song(models.Model):
    """
        Song model represents a song uploaded by a Musician
        * song_id is a 32 character key. The first 16 is the album_id this song belongs in.
        * musician_id is a ForeignKey pointing to a musician Profile (owner of song)
        * media is a fileField that
    """
    song_id = models.CharField(max_length=32, primary_key=True, editable=False)
    musician_id = models.ForeignKey(Profile)
    media = models.FileField(upload_to=user_directory_path)
    pass
