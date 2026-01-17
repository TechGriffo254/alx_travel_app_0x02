"""
Initialize Celery app for ALX Travel App.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
