import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tekhnoritm_web.settings')
app = Celery('tekhnoritm_web')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


#celery beat tasks
app.conf.beat_schedule = {
    'weekdays': {
        'task': 'order_control.tasks.send_alerts_by_dates',
        'schedule': crontab(hour=11, minute=15, day_of_week='1-5'),
    },
}
