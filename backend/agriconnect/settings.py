import os
from decouple import config

environment = config('DJANGO_ENVIRONMENT', default='development')

if environment == 'production':
    from .settings.production import *
elif environment == 'testing':
    from .settings.testing import *
else:
    from .settings.development import *
