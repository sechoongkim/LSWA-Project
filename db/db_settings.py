# Database sepecific settings.
DATABASES = {
  'default': { },
  'auth_db': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'streeTunes',
    'USER': 'appserver',
    'PASSWORD': 'foobarzoot',
    'HOST': '54.145.132.94',
    'PORT': '3306',
  },
  'db1': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'streeTunes',
    'USER': 'appserver',
    'PASSWORD': 'foobarzoot',
    'HOST': '54.145.132.94',
    'PORT': '3307',
  },
  'db2': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'streeTunes',
    'USER': 'appserver',
    'PASSWORD': 'foobarzoot',
    'HOST': '54.145.132.94',
    'PORT': '3308',
  },
}

# Database routers go here:
DATABASE_ROUTERS = ['streeTunes.routers.UserRouter']
