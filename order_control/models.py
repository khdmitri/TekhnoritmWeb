from django.db import models
from references.models import DefaultTasks
from accounts.models import Profile

# Create your models here.


class ControlConfig(models.Model):
    ref_task = models.ForeignKey(to=DefaultTasks,
                                 verbose_name='Задача',
                                 on_delete=models.CASCADE)
    is_warn_control = models.BooleanField(verbose_name='Желтый контроль включен', default=False)
    is_dang_control = models.BooleanField(verbose_name='Красный контроль включен', default=False)
    warn_days = models.IntegerField(verbose_name='Дней до включения', null=True, blank=True)
    dang_days = models.IntegerField(verbose_name='Дней до включения', null=True, blank=True)
    is_warn_alert = models.BooleanField(verbose_name='Оповещать (желтый)', default=False)
    is_dang_alert = models.BooleanField(verbose_name='Оповещать (красный)', default=False)
    warn_alert_type = models.IntegerField(verbose_name='Тип оповещения (желтый)', default=1) # 1 - однократно, 2 - каждый день
    dang_alert_type = models.IntegerField(verbose_name='Тип оповещения (красный)',
                                          default=1)  # 1 - однократно, 2 - каждый день

    @staticmethod
    def get_object_by_task(task):
        return ControlConfig.objects.filter(ref_task=task).first()

    @staticmethod
    def get_object_by_tasktype_target(tasktype, target):
        return ControlConfig.objects.filter(ref_task__task_type=tasktype).filter(ref_task__target=target).first()


class AlertPersonality(models.Model):
    ref_task = models.ForeignKey(to=ControlConfig,
                                 verbose_name='Тип контроля',
                                 on_delete=models.CASCADE)
    ref_profile = models.ForeignKey(to=Profile,
                                    verbose_name='Сотрудник',
                                    on_delete=models.CASCADE)

    @staticmethod
    def get_alerts_by_task(task):
        return AlertPersonality.objects.filter(ref_task=task)
