from django.db import models
import datetime
from orders.models import Order, Task, ExecutionPlan, Card

# Create your models here.


class ArchiveObject(models.Model):
    create_date = models.DateField(verbose_name='Дата архивации', default=datetime.date.today)
    ref_order = models.ForeignKey(to=Order,
                                  verbose_name='Заявка',
                                  on_delete=models.CASCADE,
                                  null=False,
                                  related_name='order_object')
    ref_task = models.ForeignKey(to=Task,
                                 verbose_name='Заявка',
                                 on_delete=models.CASCADE,
                                 null=False,
                                 related_name='task_object')
    ref_execution = models.ForeignKey(to=ExecutionPlan,
                                      verbose_name='Заявка',
                                      on_delete=models.CASCADE,
                                      null=False,
                                      related_name='execution_object')
    ref_card = models.ForeignKey(to=Card,
                                 verbose_name='Заявка',
                                 on_delete=models.CASCADE,
                                 null=False,
                                 related_name='card_object')
    doc_context = models.TextField(max_length=8192, blank=True, null=True)
