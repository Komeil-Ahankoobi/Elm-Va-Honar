"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# سرو فایل‌های MEDIA (روی دیسک پایدار) مستقیماً در سطح WSGI.
# این کار جدا از WhiteNoiseMiddleware (که فقط STATIC رو پوشش میده) انجام میشه،
# چون WhiteNoiseMiddleware به‌صورت پیش‌فرض فقط STATIC_ROOT رو سرو می‌کنه.
application = WhiteNoise(application)
application.add_files(settings.MEDIA_ROOT, prefix='media/')