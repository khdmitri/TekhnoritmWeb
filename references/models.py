from django.db import models
from django.db.models import Q
from django.urls import reverse
from orders.choices import TASK_TYPES, EXT_EXECUTORS, TARGET_DOC
from accounts.models import Department
from .choices import START_TYPES, FILL_TYPES, CONTRACT_TYPES
from datetime import date

# Create your models here.
TARGET_DOC_DICT = {
    'OOS': 'Расчет СЗЗ и ЗОЗ',
    'SEE': 'Санитарно-эпидемиологическая экспертиза (Р1)',
    'SEZ': 'Санитарно-эпидемиологическое заключение (Р1-РПН)',
    'PROTOCOL': 'Протокол измерений ЭМП (Р2)',
    'LETTER': 'Письмо-согласование (Р2-РПН)',
    'DOCS': 'Вручение пакета документов/Оплата',
    'EZ-R2': 'Экспертное заключние по измерениям (Р2)',
    'OTHER': 'Иное',
}


class Client(models.Model):
    short_name = models.CharField(verbose_name='Краткое наименование', max_length=256)
    long_name = models.TextField(verbose_name='Полное наименование', max_length=1024, blank=True, null=True)
    address_1 = models.TextField(verbose_name='Юридический адрес', max_length=512, blank=True, null=True)
    address_2 = models.TextField(verbose_name='Физический адрес', max_length=512, blank=True, null=True)
    inn = models.CharField(verbose_name='ИНН', max_length=64, blank=True, null=True)
    ogrn = models.CharField(verbose_name='ОГРН', max_length=64, blank=True, null=True)
    representative = models.CharField(verbose_name='Представитель', max_length=512, blank=True, null=True)
    phone = models.CharField(verbose_name='Тел. номер', max_length=128, blank=True, null=True)
    email = models.CharField(verbose_name='E-mail', max_length=256, blank=True, null=True)
    logo = models.ImageField(verbose_name='Логотип', upload_to='logo/images/',
                               default='logo/images/default_logo.jpg',
                               max_length=200, help_text='Загрузите логотип клиента, если доступно')
    is_owner = models.BooleanField(verbose_name='Является ли владельцем объектов', default=False,
                                   help_text='Если отмечено, клиент является и владельцем объектов')
    is_project = models.BooleanField(verbose_name='Является ли проектантом', default=True,
                                     help_text='Если отмечено, клиент является проектантом')

    def get_absolute_url(self):
        return reverse("references:client-detail", args=(self.id,))

    def get_parent_contracts(self):
        return Contract.objects.filter(ref_client=self).filter(is_parent=True)

    def get_available_contracts(self):
        return Contract.objects.filter(ref_client=self).filter(is_parent=True).filter(
            closed_date__isnull=True)


class Contract(models.Model):
    ref_client = models.ForeignKey(Client,
                                   verbose_name='Заказчик',
                                   on_delete=models.CASCADE)
    ref_parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    contract_type = models.CharField(verbose_name='Тип контракта', max_length=64, default='Договор', choices=CONTRACT_TYPES)
    comment = models.TextField(verbose_name='Описание', max_length=512, blank=True, null=True)
    scan_file = models.FileField(upload_to='references/contracts/',
                                 max_length=200,
                                 blank=True,
                                 null=True,
                                 help_text='Прикрепите скан договора/заказа/соглашения...')
    create_date = models.DateField(verbose_name='Дата создания', auto_now_add=True, auto_now=False)
    contract_date = models.DateField(verbose_name='Дата договора', blank=True, null=True)
    expired_date = models.DateField(verbose_name='Дата окончания', blank=True, null=True)
    closed_date = models.DateField(verbose_name='Дата закрытия', blank=True, null=True)
    doc_no = models.CharField(verbose_name='Номер договора', max_length=128, blank=True, null=True)
    is_parent = models.BooleanField(verbose_name='Родительский', default=True)

    def get_absolute_url(self):
        return reverse("references:contract-detail", args=(self.id,))

    def get_child(self):
        return Contract.objects.filter(ref_parent=self).filter(is_parent=False)

    def get_status(self):
        if self.closed_date:
            status = {
                'class': 'text-success',
                'text': 'закрыт/исполнен'
            }
        elif self.expired_date and self.expired_date < date.today():
            status = {
                'class': 'text-danger',
                'text': 'срок истек'
            }
        else:
            status = {
                'class': 'text-info',
                'text': 'действующий'
            }
        return status


class Region(models.Model):
    short_name = models.CharField(verbose_name='Центр', max_length=256)
    full_name = models.CharField(verbose_name='Регион', max_length=1024)


class RequestPerson(models.Model):
    sign_position = models.CharField(verbose_name='Должность подписанта', max_length=256, blank=True, null=True)
    sign_person = models.CharField(verbose_name='Заявления подписывает', max_length=256, blank=True, null=True)
    template = models.CharField(verbose_name='Шаблон', max_length=256, blank=True, null=True)
    regional_address = models.CharField(verbose_name='Региональный адрес', max_length=512, blank=True, null=True)
    ref_region = models.ForeignKey(to=Region,
                                   verbose_name='Регион',
                                   on_delete=models.CASCADE,
                                   null=True, blank=True)
    ref_client = models.ForeignKey(to=Client,
                                   verbose_name='Заявитель',
                                   on_delete=models.CASCADE,
                                   null=True, blank=True)

    @staticmethod
    def get_requests_by_client(client):
        return RequestPerson.objects.filter(ref_client=client)

    @staticmethod
    def get_request_by_region_client(region, client):
        collection = RequestPerson.objects.filter(ref_client=client).filter(ref_region__short_name=region)
        if collection:
            return collection.first()
        else:
            return None


class DefaultTasks(models.Model):
    task_type = models.CharField(verbose_name='Тип задачи', max_length=64, choices=TASK_TYPES)
    int_executor = models.ForeignKey(to=Department,
                                     verbose_name='Внутр. исполнитель',
                                     on_delete=models.CASCADE,
                                     null=True, blank=True)

    ext_executor = models.CharField(verbose_name='Внешний исполнитель', max_length=64, choices=EXT_EXECUTORS, null=True, blank=True)
    target = models.CharField(verbose_name='Целевой документ', max_length=64, choices=TARGET_DOC, null=True)
    start_date = models.CharField(verbose_name='Начало исполнения', max_length=64, choices=START_TYPES, null=True, blank=True)
    position = models.IntegerField(verbose_name='Позиция в списке')
    fill_type = models.IntegerField(verbose_name='Тип заполнения', default=2, choices=FILL_TYPES) # 0-Slave, 1-Lead, 2-Standalone
    title_template = models.CharField(verbose_name='Шаблон заголовка (!#)', max_length=512, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("references:default-task-detail", args=(self.id,))

    def get_target_description(self):
        return TARGET_DOC_DICT[self.target]

    @staticmethod
    def get_obj_by_target(target_name):
        objects = DefaultTasks.objects.filter(target=target_name)
        if objects:
            return objects[0]
        else:
            return None

    @staticmethod
    def get_obj_by_type(task_type):
        objects = DefaultTasks.objects.filter(task_type=task_type)
        return objects


class UniBook(models.Model):
    category = models.CharField(verbose_name='Категория', max_length=128)
    item = models.CharField(verbose_name='Запись', max_length=256, null=True, blank=True)

    @staticmethod
    def add_new_record(category, item):
        new_object = UniBook.objects.create(category=category, item=item)
        return new_object

    @staticmethod
    def get_objects_by_category(category):
        items = UniBook.objects.filter(category=category).order_by('item')
        return items


class UniBook2(models.Model):
    category = models.CharField(verbose_name='Категория', max_length=128)
    item_short = models.CharField(verbose_name='Запись', max_length=256, null=True, blank=True)
    item_long = models.CharField(verbose_name='Запись', max_length=1024, null=True, blank=True)

    @staticmethod
    def add_new_record(category, item_short, item_long):
        new_object = UniBook2.objects.create(category=category, item_short=item_short, item_long=item_long)
        return new_object

    @staticmethod
    def get_objects_by_category(category):
        items = UniBook2.objects.filter(category=category).order_by('item_short')
        return items

    @staticmethod
    def get_object_by_cat_short(category, item_short):
        items = UniBook2.objects.filter(category=category).filter(item_short=item_short)
        if items:
            return items[0]
        else:
            return None

    @staticmethod
    def get_categories():
        return UniBook2.objects.order_by('category').values('category').distinct()


class PRTOType(models.Model):
    name = models.CharField(max_length=128, verbose_name='Наименование', primary_key=True)
    order = models.IntegerField(verbose_name='Порядок', default=1)
    name_visible = models.CharField(max_length=512, verbose_name='Видимая часть')
    pdu_staff = models.CharField(max_length=256, verbose_name='ПДУ (персонал)', null=True, blank=True)
    pdu_common = models.CharField(max_length=256, verbose_name='ПДУ (население)', null=True, blank=True)
    help_text = models.CharField(max_length=512, verbose_name='Пояснение', null=True, blank=True)

    @staticmethod
    def get_types():
        return PRTOType.objects.all().order_by('order')
