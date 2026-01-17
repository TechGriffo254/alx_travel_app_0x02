"""
Celery configuration for ALX Travel App.
"""
import os
from celery import Celery
from django.conf import settings

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

# Create Celery app
app = Celery('alx_travel_app')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup."""
    print(f'Request: {self.request!r}')
