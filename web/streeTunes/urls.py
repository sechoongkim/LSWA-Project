"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from . import views
from django.contrib.auth import views as auth_views


ENCRYPTION_KEY_LENGTH = 26

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^scan/$', views.scan, name='scan'),
    url(r'^download/$', views.download, name='download'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^create-album/$', views.create_album, name='genqr'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^genqr/$', views.genqr, name='genqr'),
    url(r'^qr/(?P<pid>\w+)$', views.qr, name='qr'),
    url('^', include('django.contrib.auth.urls'))
]


