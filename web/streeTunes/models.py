from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import validators

class Musician(AbstractUser):
    musician_id = models.CharField(max_length=32, primary_key=True, editable=False)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    genre = models.CharField(max_length=10)



class Purchase(models.Model):
    # purchase_id = album_id(64) + random(64)
    purchase_id = models.CharField(max_length=128, primary_key=True, editable=False)
    time = models.DateTimeField()
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    fulfilled = models.BooleanField(default=False)
    pass

class Album(models.Model):
    # album_id = musician_id(32) + random(32)
    album_id = models.CharField(max_length=64, primary_key=True, editable=False)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    return '{0}/{1}'.format(instance.owner.id, filename)
class Song(models.Model):
    # song_id = album_id(64) + random(64)
    song_id = models.CharField(max_length=128, primary_key=True, editable=False)
    media = models.FileField(upload_to=user_directory_path)
    pass
