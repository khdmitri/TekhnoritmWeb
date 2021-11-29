from django.db import models
from references.models import UniBook2
from django.urls import reverse
from .choices import DEVICE_STATUS
from .managers import ExpiredCertificateManager
import datetime


DEVICE_STATUS_DICT = {
    'active': 'Используется',
    'inactive': 'На консервации'
}


class Pribor(models.Model):
    class Meta:
        ordering = ['category']
    name = models.CharField(max_length=256, verbose_name='Наименование')
    category = models.CharField(max_length=128, verbose_name='Категория')
    status = models.CharField(max_length=32, verbose_name='Статус', choices=DEVICE_STATUS, default='active')
    purpose = models.CharField(max_length=256, verbose_name='Назначение', null=True, blank=True)
    facility_no = models.CharField(max_length=64, verbose_name='Заводской номер', null=True, blank=True)
    produce_date = models.DateField(verbose_name='Дата выпуска', null=True, blank=True)
    reestr_no = models.CharField(max_length=64, verbose_name='No. в ресстре', null=True, blank=True)
    inv_no = models.CharField(max_length=64, verbose_name='Инвентарный номер', null=True, blank=True)
    certificate_no = models.CharField(max_length=64, verbose_name='Номер поверки', null=True, blank=True)
    certificate_date = models.DateField(verbose_name='Дата поверки', null=True, blank=True)
    certificate_place = models.CharField(max_length=64, verbose_name='Место поверки', null=True, blank=True)
    expire_date = models.DateField(verbose_name='Дата очередной поверки', null=True, blank=True)
    comment = models.CharField(max_length=256, verbose_name='Примечание', null=True, blank=True)

    limit = models.CharField(max_length=128, verbose_name='Диапазон', null=True, blank=True)
    sensitivity = models.CharField(max_length=128, verbose_name='Чувствительность', null=True, blank=True)
    accuracy = models.CharField(max_length=128, verbose_name='Погрешность', null=True, blank=True)
    unique_id = models.PositiveIntegerField(verbose_name='Уникальный идентификатор', null=True, blank=True)

    def get_status_label(self):
        if DEVICE_STATUS_DICT.get(str(self.status), None):
            return DEVICE_STATUS_DICT[str(self.status)]
        else:
            return 'Неизвестно'

    @staticmethod
    def get_data_by_status(status):
        return Pribor.objects.filter(status=status)

    def get_category_name(self):
        return UniBook2.get_object_by_cat_short('pribor_category', self.category)

    def get_absolute_url(self):
        return reverse("laboratory:pribor-detail",args=(self.id,))

    def get_date_class(self, field='expire_date', warn_days=14, danger_days=3):
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
    def get_expired(warn_days=14):
        delta_days = warn_days
        now = datetime.date.today()
        warn_date = now + datetime.timedelta(days=delta_days)
        return Pribor.objects.filter(models.Q(expire_date__lte=warn_date),
                                     models.Q(status='active'))


class ProtocolPribor(models.Model):
    ref_pribor = models.ForeignKey(to=Pribor,
                                   verbose_name='Прибор',
                                   on_delete=models.CASCADE,
                                   null=False)
    kind = models.IntegerField(verbose_name='Вид записи', default=0)

    @staticmethod
    def get_data_by_kind(kind):
        return ProtocolPribor.objects.filter(kind=kind)

    @staticmethod
    def get_pribors_by_kind(kind):
        pribors = list()
        objects = ProtocolPribor.objects.filter(kind=kind)
        for obj in objects:
            pribors.append(obj.ref_pribor)
        return pribors
