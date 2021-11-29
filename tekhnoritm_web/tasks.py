from django.core.mail import send_mail
from tekhnoritm_web.celery import app
# from .service import send
# from .models import Contact

from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time


# @app.task
# def send_spam_email(user_email):
#     send(user_email)
#
#
# @app.task
# def send_beat_email():
#     for contact in Contact.objects.all():
#         send_mail(
#             'Вы подписались на рассылку',
#             'Мы пришлем вам много спама каждые 5 минут',
#             'mambasoftgroup@gmail.com',
#             [contact.email],
#             fail_silently=False
#         )
#

@shared_task(bind=True)
def my_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += 1
        progress_recorder.set_progress(i + 1, seconds)
        print(result)
    print('Summary:', result)
    return result
