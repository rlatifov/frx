import os
import logging

from celery import Celery, Task
from celery.schedules import crontab
from frx.settings import config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frx.settings')

logger = logging.getLogger(__name__)
app = Celery('frx')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.timezone = 'Asia/Baku'
app.conf.broker_url = f'redis://{config('REDIS_HOST', 'redis')}:{config('REDIS_PORT', '6379')}/1'
app.conf.broker_connection_retry_on_startup = True

app.conf.task_track_started = True
app.conf.task_acks_on_failure_or_timeout = True
app.conf.task_acks_late = True
app.conf.result_extended = True
app.conf.result_backend = 'django-db'
app.conf.task_ignore_result = False
app.conf.result_expires = 60 * 60 * 24 * 60  # 60 days
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
app.conf.beat_schedule = {
    'get_time_series_from_twelvedata': {
        'task': 'get_time_series_from_twelvedata',
        'schedule': crontab(minute='*/2'),
        'options': {
            'expires': 60,
        }

    },
    'get_prices_from_twelvedata': {
        'task': 'get_prices_from_twelvedata',
        'schedule': crontab(minute='*/2'),
        'options': {
            'expires': 60,
        }
    },
}


class BaseTask(Task):
    max_retries = 1
    autoretry_for = (Exception,)
    default_retry_delay = 60 * 1  # 1 minutes
    # Setting retry_backoff=True adds an exponential backoff delay between retries,
    # increasing the delay with each retry.
    retry_backoff = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} failed: {exc}", exc_info=exc)
