from __future__ import absolute_import
import os
from celery import Celery
from datetime import timedelta

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourapp.settings')

app = Celery('yourapp')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Periodic Tasks Configuration
app.conf.beat_schedule = {
    'rotate-encryption-keys': {
        'task': 'products.tasks.rotate_keys',
        'schedule': timedelta(weeks=12),
        'options': {'queue': 'security'}
    },
}

app.autodiscover_tasks()