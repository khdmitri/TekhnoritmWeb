import jsonfield
from django.db import models
from django.db.models import Max
import datetime
from django.contrib.auth.models import User

from laboratory.models import Pribor
from orders.models import Order
from references.models import Client, PRTOType
from .choices import DOCUMENT_TYPES, SIGN_TYPES

# Create your models here.

SOURCE_KIND = {
    '1': 'Проектируемое оборудование',
    '2': 'Существующее оборудование',
    '3': 'Сторонее оборудование'
}


class InspectionObject(models.Model):
    ref_order = models.ForeignKey(to=Order,
                                  verbose_name='Заявка',
                                  on_delete=models.CASCADE,
                                  null=False)
    prto_type_ref = models.ForeignKey(to=PRTOType,
                                      verbose_name='Тип ПРТО',
                                      on_delete=models.CASCADE,
                                      default='Базовая станция')
    build_year = models.IntegerField(verbose_name='Год ввода', default=2020)
    build_purpose = models.CharField(verbose_name='Цель реконструкции', max_length=512, null=True, blank=True)
    name = models.CharField(verbose_name='Наименование', max_length=1024, null=True)
    address = models.CharField(verbose_name='Адрес размещения', max_length=512, null=True)
    address_fias = jsonfield.JSONField(null=True, blank=True)
    has_source = models.BooleanField(verbose_name='Имеет таблицу исх. данных', default=False)
    has_see = models.BooleanField(verbose_name='Имеет СЭЭ (Р1)', default=False)
    has_protocol = models.BooleanField(verbose_name='Имеет протокол (Р2)', default=False)
    has_ez = models.BooleanField(verbose_name='Имеет ЭЗ (Р2)', default=False)
    is_shared = models.BooleanField(verbose_name='Совместное использование', default=False)
    shared_name = models.CharField(verbose_name='Наименование объекта', max_length=256, null=True, blank=True)
    shared_standard = models.CharField(verbose_name='Стандарт', max_length=256, null=True, blank=True)
    shared_owner = models.CharField(verbose_name='Совладелец', max_length=256, null=True, blank=True)


class CommonObjectInfo(models.Model):
    ref_order = models.OneToOneField(to=Order, on_delete=models.CASCADE)

    ref_owner = models.ForeignKey(to=Client,
                                  verbose_name='Владелец',
                                  on_delete=models.CASCADE,
                                  related_name='owner',
                                  null=True, blank=True)
    ref_project = models.ForeignKey(to=Client,
                                    verbose_name='Проектант',
                                    on_delete=models.CASCADE,
                                    related_name='project',
                                    null=True, blank=True)
    project_format = models.CharField(verbose_name='Формат проекта', max_length=1024, null=True, blank=True)
    build_purpose = models.CharField(verbose_name='Цель проекта', max_length=1024, default='Новое строительство')


class SourceData(models.Model):

    ref_object = models.ForeignKey(to=InspectionObject,
                                   verbose_name='Объект',
                                   on_delete=models.CASCADE,
                                   null=False)

    kind_code = models.IntegerField(verbose_name='Код оборудования')
    kind_description = models.CharField(verbose_name='Вид оборудования', max_length=128, null=True, blank=True)
    ref_owner = models.ForeignKey(to=Client,
                                  verbose_name='Владелец',
                                  on_delete=models.CASCADE,
                                  null=True, blank=True)
    no = models.IntegerField(verbose_name='No.', null=True, blank=True)
    row_type = models.CharField(verbose_name='Тип передатчика', max_length=128, null=True, blank=True)
    power = models.CharField(verbose_name='Мощность, Вт', max_length=16, null=True, blank=True, default='20')
    qty = models.IntegerField(verbose_name='Количество', default=1)
    freq = models.CharField(verbose_name='Частота, Гц', max_length=32, null=True, blank=True)
    modulation = models.CharField(verbose_name='Модуляция', max_length=32, null=True, blank=True)
    antenna = models.CharField(verbose_name='Тип антенны', max_length=32, null=True, blank=True)
    gain = models.CharField(verbose_name='КУ', max_length=16, null=True, blank=True)
    high = models.CharField(verbose_name='Высота', max_length=16, null=True, blank=True)
    power_fact = models.CharField(verbose_name='Мощность, Вт', max_length=16, null=True, blank=True, default='20')
    dn = models.CharField(verbose_name='Диаграмма', max_length=32, null=True, blank=True)
    az_hor = models.CharField(verbose_name='Азимут, горизонт', max_length=16, null=True, blank=True)
    az_vert = models.CharField(verbose_name='Азимут, вертикаль', max_length=16, null=True, blank=True)

    @staticmethod
    def get_data_by_object_kind(ref_object, kind):
        data = SourceData.objects.filter(ref_object=ref_object).filter(kind_code=kind)
        return data

    @staticmethod
    def get_data_by_object(ref_object):
        data = SourceData.objects.filter(ref_object=ref_object)
        return data

    @staticmethod
    def get_last_no(ref_object, kind_code):
        max_value = SourceData.objects.filter(ref_object=ref_object).filter(kind_code=kind_code).aggregate(Max('no'))
        return max_value

    @staticmethod
    def get_az_by_kind(ref_object, kind_code):
        list_values = SourceData.objects.filter(ref_object=ref_object).filter(
            kind_code=kind_code).order_by().values_list('az_hor', flat=True).distinct()
        return list_values

    @staticmethod
    def get_az_by_kind_owner(ref_object, kind_code, owner):
        list_values = SourceData.objects.filter(ref_object=ref_object).filter(
            kind_code=kind_code).filter(ref_owner=owner).order_by().values_list('az_hor', flat=True).distinct()
        return list_values


class SEE(models.Model):
    see_id = models.AutoField(primary_key=True)
    ref_object = models.ForeignKey(to=InspectionObject,
                                   verbose_name='Объект',
                                   on_delete=models.CASCADE,
                                   null=False)

    see_no = models.CharField(verbose_name='СЭЭ No.', max_length=64, null=True, blank=True)
    see_date = models.DateField(verbose_name='Дата создания', default=datetime.date.today)
    standard = models.CharField(verbose_name='Стандарты', max_length=256, null=True, blank=True)
    freq = models.CharField(verbose_name='Частоты, МГц', max_length=256, null=True, blank=True)
    az = models.CharField(verbose_name='Азимуты', max_length=256, null=True, blank=True)
    project_header = models.TextField(verbose_name='Проект', max_length=512, null=True, blank=True)

    szz = models.CharField(verbose_name='СЗЗ (значение)', max_length=128, default='менее 0.3')
    unit = models.CharField(verbose_name='Ед.изм.', max_length=32, default='мкВт/см2')
    low = models.CharField(verbose_name='Нижняя граница, м', max_length=128, default='20')

    szz_description = models.TextField(verbose_name='Описание СЗЗ', max_length=1024, null=True, blank=True)
    zoz_description = models.TextField(verbose_name='Описание ЗОЗ', max_length=4096, null=True, blank=True)

    extra = models.TextField(verbose_name='Дополнительно', max_length=1024, null=True, blank=True)
    extra_staff = models.TextField(verbose_name='Обслуживающий персонал', max_length=1024, null=True, blank=True)


class EZ(models.Model):
    ez_id = models.AutoField(primary_key=True)
    ref_object = models.ForeignKey(to=InspectionObject,
                                   verbose_name='Объект',
                                   on_delete=models.CASCADE,
                                   null=False)

    ez_no = models.CharField(verbose_name='СЭЭ No.', max_length=64, null=True, blank=True)
    ez_date = models.DateField(verbose_name='Дата создания', default=datetime.date.today)
    standard = models.CharField(verbose_name='Стандарты', max_length=256, null=True, blank=True)
    freq = models.CharField(verbose_name='Частоты, МГц', max_length=256, null=True, blank=True)
    az = models.CharField(verbose_name='Азимуты', max_length=256, null=True, blank=True)

    szz = models.CharField(verbose_name='СЗЗ (значение)', max_length=128, null=True, blank=True)
    zoz = models.CharField(verbose_name='ЗОЗ (max значение)', max_length=128, null=True, blank=True)
    low = models.CharField(verbose_name='Нижняя граница, м', max_length=128, null=True, blank=True)

    szz_description = models.TextField(verbose_name='Описание СЗЗ', max_length=1024, null=True, blank=True)
    zoz_description = models.TextField(verbose_name='Описание ЗОЗ', max_length=2048, null=True, blank=True)

    extra = models.TextField(verbose_name='Дополнительно', max_length=1024, null=True, blank=True)
    extra_staff = models.TextField(verbose_name='Обслуживающий персонал', max_length=1024, null=True, blank=True)


class Protocol(models.Model):
    protocol_id = models.AutoField(primary_key=True)
    ref_object = models.ForeignKey(to=InspectionObject,
                                   verbose_name='Объект',
                                   on_delete=models.CASCADE,
                                   null=False)

    protocol_no = models.CharField(verbose_name='Протокол No.', max_length=64, null=True, blank=True)
    protocol_date = models.DateField(verbose_name='Дата создания', default=datetime.date.today)
    action_date = models.DateField(verbose_name='Дата измерения', default=datetime.date.today)
    plan_scale = models.IntegerField(verbose_name='Масштаб', default=1000)
    plan_page_count = models.IntegerField(verbose_name='Количество листов', default=1)
    standard = models.CharField(verbose_name='Стандарт', max_length=256, null=True, blank=True)
    export_date = models.DateTimeField(verbose_name='Дата экспорта', null=True, blank=True)
    export_exclude = models.BooleanField(verbose_name='Исключить из экспорта', default=False)
    export_error = models.CharField(verbose_name='Ошибка экспорта', max_length=1024, null=True, blank=True)
    pribors = models.ManyToManyField(Pribor)


class ProtocolPoints(models.Model):
    ref_protocol = models.ForeignKey(to=Protocol,
                                     verbose_name='Протокол',
                                     on_delete=models.CASCADE,
                                     null=False)
    no = models.IntegerField(verbose_name='No.', null=True, blank=True)
    no_plan = models.IntegerField(verbose_name='No.план', null=True, blank=True)
    distance = models.CharField(verbose_name='Расстояние, м', max_length=16, null=True)
    value = models.CharField(verbose_name='Значение', max_length=32, null=True)
    uncert = models.CharField(verbose_name='Неопределенность', max_length=32, default='-')
    unit = models.CharField(verbose_name='Ед.изм', max_length=32, default='мкВт/см2')
    pdu = models.CharField(verbose_name='Значение ПДУ', max_length=32, default='10')
    place = models.CharField(verbose_name='Место', max_length=256, null=True)
    high = models.CharField(verbose_name='Высота', max_length=16, null=True)
    az = models.CharField(verbose_name='Азимут', max_length=16, null=True)

    @staticmethod
    def get_points_by_protocol(proto_model):
        return ProtocolPoints.objects.filter(ref_protocol=proto_model).order_by('no')

    @staticmethod
    def get_last_no(ref_proto):
        max_value = ProtocolPoints.objects.filter(ref_protocol=ref_proto).aggregate(Max('no'))
        if max_value['no__max']:
            return max_value
        else:
            max_value['no__max'] = 0
            return max_value

    @staticmethod
    def get_last_no_plan(ref_proto):
        max_value = ProtocolPoints.objects.filter(ref_protocol=ref_proto).aggregate(Max('no_plan'))
        if max_value['no_plan__max']:
            return max_value
        else:
            max_value['no_plan__max'] = 0
            return max_value


class IncomeDocument(models.Model):
    ref_see = models.ForeignKey(to=SEE,
                                verbose_name='СЭЭ',
                                on_delete=models.CASCADE,
                                null=True, blank=True)
    short_name = models.CharField(verbose_name='Краткое наименование', max_length=64)
    presentation = models.CharField(verbose_name='Презентация', max_length=512)

    @staticmethod
    def get_docs_by_see(see_model):
        return IncomeDocument.objects.filter(ref_see=see_model)


class IncomeDocumentEZ(models.Model):
    ref_ez = models.ForeignKey(to=EZ,
                               verbose_name='ЭЗ',
                               on_delete=models.CASCADE,
                               null=True, blank=True)
    short_name = models.CharField(verbose_name='Краткое наименование', max_length=64)
    presentation = models.CharField(verbose_name='Презентация', max_length=512)

    @staticmethod
    def get_docs_by_ez(ez_model):
        return IncomeDocumentEZ.objects.filter(ref_ez=ez_model)


class EvalPoints(models.Model):
    ref_see = models.ForeignKey(to=SEE,
                                verbose_name='СЭЭ',
                                on_delete=models.CASCADE,
                                null=True, blank=True)
    no = models.IntegerField(verbose_name='No.', null=True, blank=True)
    place = models.CharField(verbose_name='Место', max_length=256, null=True, blank=True)
    no_plan = models.IntegerField(verbose_name='No.план', null=True, blank=True)
    value = models.CharField(verbose_name='Значение', max_length=32, null=True, blank=True)
    unit = models.CharField(verbose_name='Ед.изм', max_length=32, default='мкВт/см2')
    distance = models.CharField(verbose_name='Расстояние, м', max_length=16, null=True, blank=True)
    high = models.CharField(verbose_name='Высота, м', max_length=16, null=True, blank=True)
    az = models.CharField(verbose_name='Азимут, град', max_length=16, null=True, blank=True)

    @staticmethod
    def get_points_by_see(see_model):
        return EvalPoints.objects.filter(ref_see=see_model).order_by('no')

    @staticmethod
    def get_last_no(ref_see):
        max_value = EvalPoints.objects.filter(ref_see=ref_see).aggregate(Max('no'))
        return max_value

    @staticmethod
    def get_last_no_plan(ref_see):
        max_value = EvalPoints.objects.filter(ref_see=ref_see).aggregate(Max('no_plan'))
        return max_value


class ZoneByPoints(models.Model):
    ref_see = models.ForeignKey(to=SEE,
                                verbose_name='СЭЭ',
                                on_delete=models.CASCADE,
                                null=True, blank=True)
    az = models.CharField(verbose_name='Азимут, град', max_length=16, null=True, blank=True)
    high = models.CharField(verbose_name='Высота, м', max_length=16, null=True, blank=True)
    distance = models.CharField(verbose_name='Расстояние, м', max_length=16, null=True, blank=True)
    point_type = models.IntegerField(verbose_name='Тип', null=True, blank=True)
    low = models.CharField(verbose_name='Нижняя граница, м', max_length=16, null=True, blank=True)

    def get_type_description(self):
        return SOURCE_KIND[str(self.point_type)]

    @staticmethod
    def get_zone_by_see(see_model):
        return ZoneByPoints.objects.filter(ref_see=see_model)


class DocumentLow(models.Model):
    document_type = models.CharField(max_length=128, choices=DOCUMENT_TYPES)
    low_type = models.CharField(max_length=64)
    low_notation = models.CharField(max_length=128, null=True, blank=True)
    low_name = models.CharField(max_length=512, null=True, blank=True)

    @staticmethod
    def get_items_by_types(document_type, low_type):
        return DocumentLow.objects.filter(document_type=document_type).filter(low_type=low_type).order_by('id')


SIGN_TYPES_DICT = {
    'done': 'Измеряет/Исследует',
    'approved': 'Утверждает',
    'sign': 'Подписывает'
}


class DocumentSign(models.Model):
    document_type = models.CharField(max_length=128, choices=DOCUMENT_TYPES)
    sign_type = models.CharField(max_length=64, choices=SIGN_TYPES)
    ref_person = models.ForeignKey(to=User,
                                   verbose_name='Сотрудник',
                                   on_delete=models.CASCADE,
                                   null=True, blank=True)

    @staticmethod
    def get_sign_by_type(doc_type):
        return DocumentSign.objects.filter(document_type=doc_type)

    @staticmethod
    def get_sign_by_types(doc_type, sign_type):
        return DocumentSign.objects.filter(document_type=doc_type).filter(sign_type=sign_type).first()

    def get_sign_type_description(self):
        return SIGN_TYPES_DICT[str(self.sign_type)]


class ResultDocument(models.Model):
    ref_object = models.ForeignKey(to=InspectionObject,
                                   verbose_name='Объект',
                                   on_delete=models.CASCADE)
    document_type = models.CharField(max_length=128, choices=DOCUMENT_TYPES)
    attach_word = models.FileField(upload_to='inspection/doc_files/word/',
                                   max_length=200,
                                   blank=True,
                                   null=True,
                                   help_text='Прикрепите word-документ')
    attach_pdf = models.FileField(upload_to='inspection/doc_files/pdf/',
                                  max_length=200,
                                  blank=True,
                                  null=True,
                                  help_text='pdf-документ')
    pdf_signed = models.FileField(upload_to='inspection/doc_files/pdf-signed/',
                                  max_length=200,
                                  blank=True,
                                  null=True,
                                  help_text='Архивный документ')
