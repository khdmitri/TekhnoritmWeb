from django import forms

from laboratory.models import Pribor
from .models import (InspectionObject, CommonObjectInfo, SourceData, SEE, IncomeDocument, EvalPoints, ZoneByPoints,
                     DocumentSign, ResultDocument, Protocol, ProtocolPoints, EZ, IncomeDocumentEZ)


class InspectionObjectForm(forms.ModelForm):

    class Meta:
        model = InspectionObject
        fields = [
                    'id',
                    'prto_type_ref',
                    'ref_order',
                    'name',
                    'address',
                    'address_fias',
                    'build_purpose',
                    'build_year',
                    'is_shared',
                    'shared_name',
                    'shared_owner',
                    'shared_standard'
                ]
        widgets = {
            'id': forms.HiddenInput(),
            'ref_order': forms.HiddenInput(),
            'address_fias': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'placeholder': 'Наименование'}),
            'address': forms.TextInput(attrs={'placeholder': 'Адрес размещения'}),
            'shared_name': forms.TextInput(attrs={'placeholder': 'Наименование объекта'}),
            'shared_owner': forms.TextInput(attrs={'placeholder': 'Совладелец'}),
            'shared_standard': forms.TextInput(attrs={'placeholder': 'Совмещенные стандарты'}),
        }


class CommonObjectInfoForm(forms.ModelForm):

    ref_owner_text = forms.CharField(max_length=512,
                                     help_text='Поле заполнится автоматически по клику в таблице владельцев')
    ref_project_text = forms.CharField(max_length=512,
                                       help_text='Поле заполнится автоматически по клику в таблице проектантов')
    ref_owner_id = forms.IntegerField()
    ref_project_id = forms.IntegerField()
    project_format = forms.CharField(max_length=1024,
                                     help_text='Формат проекта. Поддерживается:#BSOwner(владелец ПРТО);#BSName(Наименование ПРТО);#Address(Адрес объекта);#Standard(Стандарты)')

    class Meta:
        model = CommonObjectInfo
        fields = ['ref_order',
                  'ref_owner',
                  'ref_project',
                  'ref_owner_id',
                  'ref_project_id',
                  'ref_owner_text',
                  'ref_project_text',
                  'project_format',
                  'build_purpose',
                  ]
        widgets = {
            'ref_order': forms.HiddenInput(),
            'ref_owner': forms.HiddenInput(),
            'ref_project': forms.HiddenInput(),
            'ref_owner_id': forms.HiddenInput(),
            'ref_project_id': forms.HiddenInput(),
            'ref_owner_text': forms.TextInput(attrs={'placeholder': 'Автозаполнение владельца объекта'}),
            'ref_project_text': forms.TextInput(attrs={'placeholder': 'Автозаполнение проектанта'}),
            'project_format': forms.Select(attrs={'placeholder': 'Выберите формат проекта'}),
            'build_purpose': forms.TextInput(attrs={'placeholder': 'Цель проекта'}),
        }


class SourceDataForm(forms.ModelForm):
    az_vert_sect_1 = forms.CharField(max_length=16, help_text='Вертикальный азимут (сектор 1)', required=False)
    az_hor_sect_1 = forms.CharField(max_length=16, help_text='Горизонтальный азимут (сектор 1)', required=False)
    az_vert_sect_2 = forms.CharField(max_length=16, help_text='Вертикальный азимут (сектор 2)', required=False)
    az_hor_sect_2 = forms.CharField(max_length=16, help_text='Горизонтальный азимут (сектор 2)', required=False)
    az_vert_sect_3 = forms.CharField(max_length=16, help_text='Вертикальный азимут (сектор 3)', required=False)
    az_hor_sect_3 = forms.CharField(max_length=16, help_text='Горизонтальный азимут (сектор 3)', required=False)
    owner_id = forms.IntegerField(required=False)
    owner_name = forms.CharField(max_length=256, help_text='При выборе владельца, поле заполнится автоматически',
                                 required=False)

    class Meta:
        model = SourceData
        fields = [
            'id',
            'ref_object',
            'kind_code',
            'kind_description',
            'no',
            'row_type',
            'power',
            'qty',
            'freq',
            'modulation',
            'antenna',
            'gain',
            'high',
            'power_fact',
            'dn',
            'ref_owner',
            'owner_id',
            'owner_name'
        ]
        widgets = {
            'ref_object': forms.HiddenInput(),
            'id': forms.HiddenInput(),
            'ref_owner': forms.HiddenInput(),
            'owner_id': forms.HiddenInput(),
            'kind_code': forms.HiddenInput(),
            'kind_description': forms.HiddenInput(),
            'no': forms.TextInput(attrs={'readonly': True})
        }


class SEEForm(forms.ModelForm):

    class Meta:
        model = SEE
        fields = [
            'see_id',
            'ref_object',
            'see_no',
            'see_date',
            'standard',
            'freq',
            'az',
            'project_header',
            'szz_description',
            'zoz_description',
            'extra'
        ]
        widgets = {
            'see_id': forms.HiddenInput(),
            'ref_object': forms.HiddenInput(),
            'standard': forms.TextInput(attrs={'placeholder': 'Стандарты'}),
            'freq': forms.TextInput(attrs={'placeholder': 'Частоты'}),
            'az': forms.TextInput(attrs={'placeholder': 'Азимуты'}),
            'extra': forms.TextInput(attrs={'placeholder': 'Дополнительно'})
        }

        see_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата документа'}
        ),
            input_formats='%d.%m.%Y'
        )


class EZForm(forms.ModelForm):

    class Meta:
        model = EZ
        fields = [
            'ez_id',
            'ref_object',
            'ez_no',
            'ez_date',
            'standard',
            'freq',
            'az',
            'szz_description',
            'zoz_description',
            'extra'
        ]
        widgets = {
            'ez_id': forms.HiddenInput(),
            'ref_object': forms.HiddenInput(),
            'standard': forms.TextInput(attrs={'placeholder': 'Стандарты'}),
            'freq': forms.TextInput(attrs={'placeholder': 'Частоты'}),
            'az': forms.TextInput(attrs={'placeholder': 'Азимуты'}),
            'extra': forms.TextInput(attrs={'placeholder': 'Дополнительно'})
        }

        ez_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата документа'}
        ),
            input_formats='%d.%m.%Y'
        )


class CustomPriborSelection(forms.ModelMultipleChoiceField):
    def label_from_instance(self, member):
        return '%s' % member.name


class ProtocolForm(forms.ModelForm):
    pribors = CustomPriborSelection(
        queryset=Pribor.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Protocol
        fields = [
            'ref_object',
            'protocol_id',
            'protocol_no',
            'protocol_date',
            'action_date',
            'plan_scale',
            'plan_page_count',
            'standard',
            'pribors',
        ]
        widgets = {
            'ref_object': forms.HiddenInput(),
            'protocol_id': forms.HiddenInput(),
        }

        protocol_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата документа'}
        ),
            input_formats='%d.%m.%Y'
        )

        action_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата измерений'}
        ),
            input_formats='%d.%m.%Y'
        )


class SZZZoneForm(forms.ModelForm):
    is_detailed_gen = forms.BooleanField(required=False,
                                         help_text='Если отмечено, будет генерировать подробно по всем азимутам, включая сторонние')

    class Meta:
        model = SEE
        fields = [
            'see_id',
            'ref_object',
            'szz',
            'is_detailed_gen',
            'szz_description',
            'zoz_description',
            'unit'
        ]
        widgets = {
            'see_id': forms.HiddenInput(),
            'ref_object': forms.HiddenInput(),
            'szz': forms.TextInput(attrs={'placeholder': 'СЗЗ (значение)'}),
            'unit': forms.TextInput(attrs={'placeholder': 'Ед.изм.'}),
            'szz_description': forms.TextInput(attrs={'placeholder': 'Описание СЗЗ'}),
            'zoz_description': forms.TextInput(attrs={'placeholder': 'Описание ЗОЗ'}),
        }


class SZZZoneEZForm(forms.ModelForm):
    is_detailed_gen = forms.BooleanField(required=False,
                                         help_text='Если отмечено, будет генерировать подробно по всем азимутам, включая сторонние')

    class Meta:
        model = EZ
        fields = [
            'ez_id',
            'ref_object',
            'is_detailed_gen',
            'szz_description',
            'zoz_description',
            'szz',
        ]
        widgets = {
            'see_id': forms.HiddenInput(),
            'ref_object': forms.HiddenInput(),
            'szz': forms.TextInput(attrs={'placeholder': 'СЗЗ (значение)'}),
            'szz_description': forms.TextInput(attrs={'placeholder': 'Описание СЗЗ'}),
            'zoz_description': forms.TextInput(attrs={'placeholder': 'Описание ЗОЗ'}),
        }


class IncomeDocumentForm(forms.ModelForm):

    class Meta:
        model = IncomeDocument
        fields = ['ref_see', 'short_name', 'presentation']
        widgets = {
            'ref_see': forms.HiddenInput(),
            'short_name': forms.TextInput(attrs={'placeholder': 'Краткое наименование'}),
            'presentation': forms.TextInput(attrs={'placeholder': 'Представление'}),
        }


class IncomeDocumentEZForm(forms.ModelForm):

    class Meta:
        model = IncomeDocumentEZ
        fields = ['ref_ez', 'short_name', 'presentation']
        widgets = {
            'ref_ez': forms.HiddenInput(),
            'short_name': forms.TextInput(attrs={'placeholder': 'Краткое наименование'}),
            'presentation': forms.TextInput(attrs={'placeholder': 'Представление'}),
        }


class ExtraForm(forms.ModelForm):

    class Meta:
        model = SEE
        fields = [
            'see_id',
            'ref_object',
            'extra',
            'extra_staff'
        ]
        widgets = {
            'see_id': forms.HiddenInput(),
            'ref_object': forms.HiddenInput(),
            'extra': forms.TextInput(attrs={'placeholder': 'Описание размещения оборудования'}),
            'extra_staff': forms.Textarea(attrs={'rows': 5})
        }


class ExtraEZForm(forms.ModelForm):

    class Meta:
        model = EZ
        fields = [
            'ez_id',
            'ref_object',
            'extra',
            'extra_staff'
        ]
        widgets = {
            'ez_id': forms.HiddenInput(),
            'ref_object': forms.HiddenInput(),
            'extra': forms.TextInput(attrs={'placeholder': 'Описание размещения оборудования'}),
            'extra_staff': forms.Textarea(attrs={'rows': 5})
        }


class EvalPointsForm(forms.ModelForm):

    class Meta:
        model = EvalPoints
        fields = ['ref_see', 'place', 'no_plan', 'value', 'unit', 'distance', 'high', 'az']
        widgets = {
            'ref_see': forms.HiddenInput(),
            'place': forms.TextInput(attrs={'placeholder': 'Место'}),
            'no_plan': forms.NumberInput(attrs={'placeholder': 'No.план'}),
            'value': forms.TextInput(attrs={'placeholder': 'Значение'}),
            'unit': forms.TextInput(attrs={'placeholder': 'Ед.измерения'}),
            'distance': forms.TextInput(attrs={'placeholder': 'Расстояние'}),
            'high': forms.TextInput(attrs={'placeholder': 'Высота'}),
            'az': forms.TextInput(attrs={'placeholder': 'Азимут'}),
        }


class ProtocolPointsForm(forms.ModelForm):

    class Meta:
        model = ProtocolPoints
        fields = ['ref_protocol', 'place', 'no_plan', 'value', 'uncert', 'unit', 'distance', 'high', 'pdu', 'az']
        widgets = {
            'ref_protocol': forms.HiddenInput(),
            'place': forms.TextInput(attrs={'placeholder': 'Место'}),
            'no_plan': forms.NumberInput(attrs={'placeholder': 'No.план'}),
            'value': forms.TextInput(attrs={'placeholder': 'Значение'}),
            'uncert': forms.TextInput(attrs={'placeholder': 'Неопределенность'}),
            'unit': forms.TextInput(attrs={'placeholder': 'Ед.измерения'}),
            'distance': forms.TextInput(attrs={'placeholder': 'Расстояние'}),
            'high': forms.TextInput(attrs={'placeholder': 'Высота'}),
            'pdu': forms.TextInput(attrs={'placeholder': 'Значение ПДУ'}),
            'az': forms.TextInput(attrs={'placeholder': 'Азимут'}),
        }


class ZoneForm(forms.ModelForm):

    class Meta:
        model = ZoneByPoints
        fields = ['id', 'ref_see', 'distance', 'high', 'az', 'low']
        widgets = {
            'id': forms.HiddenInput(),
            'ref_see': forms.HiddenInput(),
            'distance': forms.TextInput(attrs={'placeholder': 'Расстояние'}),
            'high': forms.TextInput(attrs={'placeholder': 'Высота'}),
            'az': forms.TextInput(attrs={'placeholder': 'Азимут'}),
            'low': forms.TextInput(attrs={'placeholder': 'Нижняя граница'}),
        }


class DocumentSignForm(forms.ModelForm):
    ref_person_text = forms.CharField(max_length=512,
                                      help_text='Поле заполнится автоматически по клику в таблице сотрудников')

    class Meta:
        model = DocumentSign
        fields = ['document_type', 'sign_type', 'ref_person']
        widgets = {
            'ref_person': forms.HiddenInput(),
            'document_type': forms.HiddenInput(),
        }


class ResultDocumentForm(forms.ModelForm):

    class Meta:
        model = ResultDocument
        fields = ['id', 'document_type', 'attach_word', 'pdf_signed']
        widgets = {
            'id': forms.HiddenInput(),
            'document_type': forms.HiddenInput(),
        }
