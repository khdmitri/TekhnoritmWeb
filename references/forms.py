from django import forms
from .models import Client, DefaultTasks, UniBook2, RequestPerson, Contract


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ['id', 'short_name', 'long_name', 'address_1', 'address_2', 'inn', 'ogrn', 'representative', 'phone',
                  'email', 'logo', 'is_owner', 'is_project']
        widgets = {
            'id': forms.HiddenInput(),
            'short_name': forms.TextInput(attrs={'placeholder': 'Краткое наименование'}),
            'long_name': forms.TextInput(attrs={'placeholder': 'Полное наименование'}),
            'address_1': forms.TextInput(attrs={'placeholder': 'Юридический адрес'}),
            'address_2': forms.TextInput(attrs={'placeholder': 'Фактический адрес'}),
            'inn': forms.TextInput(attrs={'placeholder': 'ИНН'}),
            'ogrn': forms.TextInput(attrs={'placeholder': 'ОГРН'}),
            'representative': forms.TextInput(attrs={'placeholder': 'Представитель'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Номер телефона'}),
            'email': forms.TextInput(attrs={'placeholder': 'E-mail'}),
        }


class ContractForm(forms.ModelForm):
    client_id = forms.IntegerField()
    client_name = forms.CharField(max_length=256, help_text='При выборе клиента, поле заполнится автоматически')

    class Meta:
        model = Contract
        fields = ['id', 'doc_no', 'contract_type', 'comment', 'scan_file', 'contract_date', 'expired_date',
                  'closed_date', 'ref_parent', 'is_parent'] + \
                 ['client_id', 'client_name', ]
        widgets = {
            'id': forms.HiddenInput(),
            'client_id': forms.HiddenInput(),
            'ref_client': forms.HiddenInput(),
            'comment': forms.TextInput(attrs={'placeholder': 'Номер оригинальной заявки',
                                              'rows': 3}),
        }

        contract_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата договора'}
        ),
            input_formats='%d.%m.%Y'
        )

        expired_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата окончания'}
        ),
            input_formats='%d.%m.%Y'
        )

        closed_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата закрытия'}
        ),
            input_formats='%d.%m.%Y'
        )


class DefaultTaskForm(forms.ModelForm):

    class Meta:
        model = DefaultTasks
        fields = ['id', 'task_type', 'int_executor', 'ext_executor', 'target', 'start_date', 'position', 'fill_type',
                  'title_template']
        widgets = {
            'id': forms.HiddenInput(),
            'task_type': forms.HiddenInput(),
            'int_executor': forms.Select(attrs={'placeholder': 'Внутреннее подразделение'}),
            'ext_executor': forms.Select(attrs={'placeholder': 'Внешний исполнитель'}),
            'target': forms.Select(attrs={'placeholder': 'Целевой документ'}),
            'fill_type': forms.Select(attrs={'placeholder': 'Тип заполнения'}),
            'start_date': forms.Select(attrs={'placeholder': 'Начало исполнения'}),
            'position': forms.NumberInput(attrs={'placeholder': 'Позиция'}),
            'title_template': forms.Textarea(attrs={'rows': 5}),
        }


class UniBook2Form(forms.ModelForm):

    class Meta:
        model = UniBook2
        fields = ['id', 'category', 'item_short', 'item_long']
        widget = {
            'id': forms.HiddenInput(),
            'category': forms.HiddenInput(),
            'item_short': forms.TextInput(attrs={'placeholder': 'Короткое наименование'}),
            'long_short': forms.TextInput(attrs={'placeholder': 'Полное наименование'}),
        }


class RequestPersonForm(forms.ModelForm):

    class Meta:
        model = RequestPerson
        fields = ['id', 'sign_person', 'sign_position', 'template', 'regional_address','ref_client', 'ref_region']
        widget = {
            'id': forms.HiddenInput(),
            'ref_client': forms.HiddenInput(),
            'sign_person': forms.TextInput(attrs={'placeholder': 'ФИО'}),
            'sign_position': forms.TextInput(attrs={'placeholder': 'Должность'}),
            'template': forms.TextInput(attrs={'placeholder': 'Шаблон'}),
            'regional_address': forms.TextInput(attrs={'placeholder': 'Региональный адрес'}),
            'ref_region': forms.Select(attrs={'placeholder': 'Выберите регион'})
        }