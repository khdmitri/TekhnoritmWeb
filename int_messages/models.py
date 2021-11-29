from django.db import models
from accounts.models import Department, Profile
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your models here.


class Message(models.Model):
    create_date = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    sender = models.ForeignKey(get_user_model(),
                               verbose_name='Отправитель',
                               related_name='user_sender',
                               on_delete=models.CASCADE,
                               null=False)
    receiver_staff = models.ForeignKey(get_user_model(),
                                       verbose_name='Получатель',
                                       related_name='user_receiver',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True,
                                       help_text='Выберите сотрудника-получателя или оставьте пустым, чтобы отправить всем')
    receiver_department = models.ForeignKey(Department,
                                            verbose_name='Получатель-Подразделение',
                                            on_delete=models.CASCADE,
                                            null=True,
                                            blank=True,
                                            help_text='Выберите отдел получения или оставьте пустым, чтобы отправить всем')
    unread = models.BooleanField(verbose_name='Новое', default=True)
    topic = models.CharField(verbose_name='Тема', max_length=200)
    body = models.TextField(verbose_name='Текст сообщения', max_length=1024)
    ticket_id = models.IntegerField(verbose_name='Номер темы', blank=True, null=True)
    closed = models.BooleanField(default=False)
    attach = models.FileField(upload_to='messages_attach/',
                              max_length=200,
                              blank=True,
                              null=True,
                              help_text='Прикрепите файл, если требуется...')

    @staticmethod
    def get_outbox(sender, limit=30):
        qs = Message.objects.filter(sender=sender).exclude(
            closed=True
        ).order_by('create_date')[:limit]
        return qs

    @staticmethod
    def get_inbox(profile, limit=30):
        qs_department = Message.objects.filter(
            receiver_department=profile.department).exclude(
            receiver_staff__isnull=False
        ).exclude(
            closed=True
        ).order_by('create_date')[:limit]
        qs_personal = Message.objects.filter(
            receiver_staff=profile.user
        ).exclude(
            closed=True
        ).order_by('create_date')[:limit]
        return {
            'department': qs_department,
            'personal': qs_personal,
        }

    @staticmethod
    def get_new_messages(profile, limit=10):
        qs_department = Message.objects.filter(
            receiver_department=profile.department).exclude(
            receiver_staff__isnull=False
        ).exclude(
            closed=True
        ).exclude(
            unread=False
        ).order_by('create_date')[:limit]
        qs_personal = Message.objects.filter(
            receiver_staff=profile.user
        ).exclude(
            closed=True
        ).exclude(
            unread=False
        ).order_by('create_date')[:limit]
        return {
            'department': qs_department,
            'personal': qs_personal,
        }

    @staticmethod
    def get_messages_by_ticket(ticket_id, message_id):
        if message_id is not None:
            qs = Message.objects.filter(
                ticket_id=ticket_id
            ).exclude(
                id=message_id
            ).order_by('create_date')
        else:
            qs = Message.objects.filter(
                ticket_id=ticket_id
            ).order_by('create_date')
        return qs

    def get_absolute_url(self):
        return reverse("int_messages:message-detail", args=(self.id, 'inbox', ))


class Alert(models.Model):
    create_date = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    code = models.IntegerField(verbose_name='Код сообщения')
    action_url = models.CharField(verbose_name='Ссылка на действие', max_length=256, null=True, blank=True)
    alert_code = models.CharField(verbose_name='Код оповещения', max_length=128, null=True, blank=True)
    receiver_position = models.ForeignKey(Profile,
                                          verbose_name='Получатель-сотрудник',
                                          on_delete=models.CASCADE,
                                          null=True,
                                          blank=True)
    receiver_department = models.ForeignKey(Department,
                                            verbose_name='Получатель-Подразделение',
                                            on_delete=models.CASCADE,
                                            null=True,
                                            blank=True)
    unread = models.BooleanField(verbose_name='Новое', default=True)
    topic = models.CharField(verbose_name='Тема', max_length=200)
    body = models.TextField(verbose_name='Текст сообщения', max_length=1024)
    closed = models.BooleanField(default=False)

    @staticmethod
    def get_alerts_by_alert_code(alert_code):
        return Alert.objects.filter(alert_code=alert_code)

    @staticmethod
    def get_new_alerts(profile, limit=10):
        qs_department = Alert.objects.filter(
            receiver_department=profile.department).exclude(
            receiver_position__isnull=False
        ).exclude(
            closed=True
        ).exclude(
            unread=False
        ).order_by('-create_date')[:limit]
        qs_personal = Alert.objects.filter(
            receiver_position=profile
        ).exclude(
            closed=True
        ).exclude(
            unread=False
        ).order_by('-create_date')[:limit]
        return {
            'department': qs_department,
            'personal': qs_personal,
        }

    @staticmethod
    def get_alert_by_code_body_date(check_date, code, body):
        return Alert.objects.filter(create_date__gte=check_date).filter(code=code).filter(body=body)

    def get_absolute_url(self):
        return reverse("int_messages:alert-detail", args=(self.id,))
