import os
from celery import Celery
from .celery_schedule import beat_schedule
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "togoScrap.settings")
app = Celery("togoScrap")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(['scrapper'])

app.conf.beat_schedule = beat_schedule

