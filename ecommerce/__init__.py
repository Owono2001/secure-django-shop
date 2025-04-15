import sys

try:
    from patches import baseconv
    sys.modules["django.utils.baseconv"] = baseconv
except ImportError:
    raise ImportError("Neither django.utils.baseconv nor patches.baseconv could be imported")

from .celery import app as celery_app

__all__ = ('celery_app',)