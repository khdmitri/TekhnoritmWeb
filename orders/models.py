from django.db import models
from references.models import Client, Contract
from accounts.models import Department
from order_control.models import ControlConfig
from .choices import TASK_TYPES, EXT_EXECUTORS, TARGET_DOC, REGIONS
from django.urls import reverse
import datetime

# Create your models here.

TASK_TYPES_DICT = {
    'R1':"Работы по схеме Р1",
    'R2': "Работы по схеме Р2",
    'PK-PRTO': "Производственный контроль (ПРТО)",
    'PK': "Производственный контроль (лаборатория)",
    'SOUT': "СОУТ",
    'OTHER': "Иное",
}


TARGET_DOC_DICT = {
    'OOS': 'Расчет СЗЗ и ЗОЗ',
    'SEE': 'Санитарно-эпидемиологическая экспертиза (Р1)',
    'SEZ': 'Санитарно-эпидемиологическое заключение (Р1-РПН)',
    'PROTOCOL': 'Протокол измерений ЭМП (Р2)',
    'LETTER': 'Письмо-согласование (Р2-РПН)',
    'DOCS': 'Вручение пакета документов/Оплата',
    'EZ-R2': 'Экспертное заключние по измерениям (Р2)',
    'OTHER': 'Иное',
    'none': 'Не установлен'
}


class Order(models.Model):
    order_id = models.CharField(verbose_name='No.заявки', max_length=32, primary_key=True,
                                help_text='Номер генерируется по нажатию кнопки генерировать...')
    ext_order_id = models.CharField(verbose_name='No. оригинальной заявки', max_length=32, null=True, blank=True,
                                    help_text='Номер оригинальной заявки')
    description = models.TextField(verbose_name='Описание', max_length=512, null=True, blank=True,)
    create_date = models.DateField(verbose_name='Дата создания', auto_now_add=True, auto_now=False)
    close_date = models.DateField(verbose_name='Дата закрытия', blank=True, null=True)
    dead_line = models.DateField(verbose_name='Дата исполнения', null=True, blank=True,
                                     help_text='Дата исполнения (до)')
    client = models.ForeignKey(to=Client,
                               verbose_name='Заявитель',
                               on_delete=models.CASCADE,
                               null=True, blank=True,)
    contracts = models.ManyToManyField(Contract)
    is_public = models.BooleanField(verbose_name='Опубликована', default=False)
    master_id = models.CharField(verbose_name='No.Мастер-Заявки', max_length=32,
                                 null=True, blank=True)
    region = models.CharField(verbose_name='Регион', max_length=200, choices=REGIONS, default='Ульяновск')
    img = models.ImageField(verbose_name='Изображение', upload_to='orders/images/', max_length=200,
                            help_text='Добавьте изображение заявки, если имеется...', null=True, blank=True)

    def get_absolute_url(self):
        return reverse("orders:order-detail",args=(self.order_id,))

    def get_date_class(self, field='dead_line', warn_days=7, danger_days=2):
        now = datetime.date.today()
        warn_date = now + datetime.timedelta(days=warn_days)
        danger_date = now + datetime.timedelta(days=danger_days)
        el_class = ''
        try:
            if hasattr(self, field):
                if getattr(self, field) <= danger_date:
                    print(str(getattr(self, field)))
                    print(str(danger_date))
                    el_class = 'text-danger font-weight-bold'
                elif getattr(self, field) <= warn_date:
                    el_class = 'text-warning font-weight-bold'
                else:
                    el_class = 'text-success'
        except Exception as e:
            print('get_date_class:', str(e))
            el_class = ''

        return el_class

    @staticmethod
    def get_slaves(master_order):
        orders = Order.objects.filter(master_id=master_order.order_id)
        return orders


class Task(models.Model):
    task_id = models.CharField(verbose_name='No.внут.заявки', max_length=32, primary_key=True)
    ref_order = models.ForeignKey(to=Order,
                                  verbose_name='Заявка',
                                  on_delete=models.CASCADE,
                                  null=False)
    distribution_dep = models.ForeignKey(to=Department,
                                         verbose_name='Распределитель',
                                         on_delete=models.CASCADE,
                                         null=True)
    task_type = models.CharField(verbose_name='Тип задачи', max_length=64, choices=TASK_TYPES)
    qty = models.IntegerField(verbose_name='Количество', default=1)
    description = models.TextField(verbose_name='Описание', max_length=512, null=True, blank=True)
    create_date = models.DateField(verbose_name='Дата создания', auto_now_add=True, auto_now=False)
    close_date = models.DateField(verbose_name='Дата закрытия', null=True, blank=True)
    dead_line = models.DateField(verbose_name='Дата исполнения', null=True)
    accept_date = models.DateField(verbose_name='Дата принятия', null=True, blank=True)
    attach = models.FileField(upload_to='orders/task_files/',
                              max_length=200,
                              blank=True,
                              null=True,
                              help_text='Прикрепите архив с исходными данными, если имеются...')

    def get_absolute_url(self):
        return reverse("orders:order-task-detail", args=(self.task_id,))

    def get_task_description(self):
        return '%s' % (TASK_TYPES_DICT[str(self.task_type)])

    @staticmethod
    def get_tasks_by_order(ref_order):
        return Task.objects.filter(ref_order=ref_order)

    def get_date_class(self, field='dead_line', warn_days=7, danger_days=2):
        now = datetime.date.today()
        warn_date = now + datetime.timedelta(days=warn_days)
        danger_date = now + datetime.timedelta(days=danger_days)
        el_class = ''
        try:
            if hasattr(self, field):
                if getattr(self, field) <= danger_date:
                    print(str(getattr(self, field)))
                    print(str(danger_date))
                    el_class = 'text-danger font-weight-bold'
                elif getattr(self, field) <= warn_date:
                    el_class = 'text-warning font-weight-bold'
                else:
                    el_class = 'text-success'
        except Exception as e:
            print('get_date_class:', str(e))
            el_class = ''

        return el_class


EXT_EXECUTORS_DICT = {
    'RPN': 'Роспотребнадзор',
    'FMBA': 'ФМБА',
    'OWNER': 'Владелец ПРТО',
    'СLIENT': 'Заказчик',
    'OTHER': 'Иное',
}


class ExecutionPlan(models.Model):
    ref_task = models.ForeignKey(to=Task,
                                 verbose_name='Задача',
                                 on_delete=models.CASCADE,
                                 null=False
                                 )
    int_executor = models.ForeignKey(to=Department,
                                   verbose_name='Внутр. исполнитель',
                                   on_delete=models.CASCADE,
                                   null=True, blank=True)

    ext_executor = models.CharField(verbose_name='Внешний исполнитель', max_length=64, choices=EXT_EXECUTORS, null=True, blank=True)
    target = models.CharField(verbose_name='Целевой документ', max_length=64, choices=TARGET_DOC, null=True)
    extra = models.CharField(verbose_name='Дополнительно', max_length=256, null=True, blank=True)
    start_date = models.DateField(verbose_name='Начало', null=True, blank=True)
    stop_date = models.DateField(verbose_name='Окончание', null=True, blank=True)
    position = models.IntegerField(verbose_name='Позиция в списке')
    description = models.TextField(verbose_name='Описание', max_length=512, null=True, blank=True)
    is_distributed = models.BooleanField(verbose_name='Если распределено', default=False)
    plan_type = models.IntegerField(verbose_name='Тип стадии', default=0) # 1 - Lead position; 2 - Standalone; 0 - Slave position

    def get_absolute_url(self):
        return reverse("orders:action-detail",args=(self.id,))

    def get_execution_url(self):
        return reverse('orders:action-execute', args=(self.id,))

    def get_executor(self):
        if EXT_EXECUTORS_DICT.get(self.ext_executor, None):
            return EXT_EXECUTORS_DICT[self.ext_executor]
        else:
            return None

    def get_target_description(self):
        return TARGET_DOC_DICT[self.target]

    def get_progress(self):
        qty = self.ref_task.qty
        ready_cards = Card.get_cards_by_action(self)
        ready_qty = 0
        for card in ready_cards:
            if card.source_file or card.archive_file:
                ready_qty += card.doc_qty

        return {'ready': ready_qty, 'from': qty}

    def get_date_class(self, field='start_date'):
        now = datetime.date.today()
        cc = ControlConfig.get_object_by_tasktype_target(self.ref_task.task_type, self.target)
        el_class = ''
        try:
            if hasattr(self, field):
                warn_date = getattr(self, field) + datetime.timedelta(days=cc.warn_days)
                danger_date = getattr(self, field) + datetime.timedelta(days=cc.dang_days)

                if now >= danger_date:
                    el_class = 'text-danger font-weight-bold'
                elif now >= warn_date:
                    el_class = 'text-warning font-weight-bold'
                else:
                    el_class = 'text-success'
        except Exception as e:
            print('get_date_class:', str(e))
            el_class = ''

        return el_class

    def get_duration(self, field='start_date'):
        now = datetime.date.today()
        duration = -1
        try:
            if hasattr(self, field):
                delta = now - getattr(self, field)
                duration = delta.days
        except Exception as e:
            print('get_duration:', str(e))
            duration = -1

        return duration

    @staticmethod
    def get_actions_by_task(task_id):
        return ExecutionPlan.objects.filter(ref_task=task_id)


class Card(models.Model):
    execution_id = models.AutoField(primary_key=True)
    ref_action = models.ForeignKey(to=ExecutionPlan,
                                    verbose_name='Работа',
                                    on_delete=models.CASCADE,
                                    null=False
                                  )
    start_date = models.DateField(verbose_name='Старт дата', null=True, blank=True)
    stop_date = models.DateField(verbose_name='Стоп дата', null=True, blank=True)
    object_id = models.IntegerField(verbose_name='Идентификатор объекта', null=True, blank=True)
    object_full_name = models.TextField(verbose_name='Название', max_length=1024, null=True, blank=True)
    doc_no = models.CharField(verbose_name='Номер документа', max_length=64, null=True, blank=True)
    doc_date = models.DateField(verbose_name='Дата', null=True, blank=True)
    doc_type = models.CharField(verbose_name='Целевой тип', max_length=256, choices=TARGET_DOC, default='none')
    doc_title = models.TextField(verbose_name='Название', max_length=256, null=True, blank=True)
    doc_base = models.CharField(verbose_name='База', max_length=1024, null=True, blank=True)
    doc_qty = models.IntegerField(verbose_name='Количество документов', default=1)

    source_file = models.FileField(upload_to='orders/execution_files/sources/',
                              max_length=200,
                              blank=True,
                              null=True,
                              help_text='Прикрепите исходный документ, если имеется...')

    archive_file = models.FileField(upload_to='orders/execution_files/archive/',
                              max_length=200,
                              blank=True,
                              null=True,
                              help_text='Прикрепите архивный документ, если имеется...')

    def get_formatted_date(self):
        if self.doc_date:
            return self.doc_date.strftime('%d.%m.%Y')
        else:
            return None

    def get_absolute_url(self):
        return reverse("orders:card-detail",args=(self.execution_id,))

    @staticmethod
    def get_cards_by_action(action):
        return Card.objects.filter(ref_action=action)

    @staticmethod
    def get_leader_cards(action_obj):
        cards = Card.objects.filter(ref_action__ref_task__ref_order=action_obj.ref_task.ref_order).filter(
                                    ref_action__ref_task=action_obj.ref_task).filter(
                                    ref_action__plan_type=1)
        return cards

    def get_doc_type_description(self):
        if TARGET_DOC_DICT.get(str(self.doc_type), None):
            return TARGET_DOC_DICT[str(self.doc_type)]
        else:
            return None

    @staticmethod
    def get_card_by_object_target(object_id, target):
        card = Card.objects.filter(object_id=object_id).filter(doc_type=target).first()
        return card
