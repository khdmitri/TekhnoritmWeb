from django import forms
from .models import Order, Task, ExecutionPlan, Card


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['order_id', 'ext_order_id', 'region', 'description', 'dead_line', 'img']
        widgets = {
            'order_id': forms.HiddenInput(),
            'ext_order_id': forms.TextInput(attrs={'placeholder': 'Номер оригинальной заявки'}),
            'region': forms.Select(attrs={'placeholder': 'Регион'}),
            'description': forms.TextInput(attrs={'placeholder': 'Описание'}),
        }

        dead_line = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Срок до'}
        ),
            input_formats='%d.%m.%Y'
        )


class OrderCreateForm(forms.ModelForm):
    client_id = forms.IntegerField()
    client_name = forms.CharField(max_length=256, help_text='При выборе клиента, поле заполнится автоматически')

    class Meta:
        model = Order
        fields = ['order_id', 'ext_order_id', 'region', 'description', 'dead_line', 'img', 'client'] + ['client_id', 'client_name']
        widgets = {
            'order_id': forms.TextInput(attrs={'placeholder': 'Номер заявки'}),
            'ext_order_id': forms.TextInput(attrs={'placeholder': 'Номер оригинальной заявки'}),
            'region': forms.Select(attrs={'placeholder': 'Регион'}),
            'description': forms.TextInput(attrs={'placeholder': 'Описание'}),
            'client': forms.HiddenInput(),

            'client_id': forms.HiddenInput()
        }

        dead_line = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Срок до'}
        ),
            input_formats='%d.%m.%Y'
        )


class OrderTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['task_id', 'ref_order', 'task_type', 'qty', 'description', 'dead_line', 'attach']
        widgets = {
            'task_id': forms.TextInput(attrs={'placeholder': 'Номер внутренней заявки'}),
            'task_type': forms.Select(attrs={'placeholder': 'Выберите тип исполнения'}),
            'qty': forms.NumberInput(attrs={'placeholder': 'Количество'}),
            'description': forms.TextInput(attrs={'placeholder': 'Описание'}),
            'ref_order': forms.HiddenInput(),
        }

        dead_line = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Срок до'}
        ),
            input_formats='%d.%m.%Y'
        )


class OrderTaskEditForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['task_id', 'task_type', 'qty', 'description', 'dead_line', 'attach', 'ref_order']
        widgets = {
            'task_id': forms.HiddenInput(),
            'task_type': forms.HiddenInput(),
            'qty': forms.NumberInput(attrs={'placeholder': 'Количество'}),
            'description': forms.TextInput(attrs={'placeholder': 'Описание'}),
            'ref_order': forms.HiddenInput(),
        }

        dead_line = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Срок до'}
        ),
            input_formats='%d.%m.%Y'
        )


class ExecutionPlanForm(forms.ModelForm):
    class Meta:
        model = ExecutionPlan
        fields = ['ref_task', 'int_executor', 'ext_executor', 'target', 'extra', 'start_date', 'position', 'description']
        widgets = {
            'ref_task': forms.HiddenInput(),
            'int_executor': forms.Select(attrs={'placeholder': 'Внутренний исполнитель'}),
            'ext_executor': forms.Select(attrs={'placeholder': 'Внешний исполнитель'}),
            'target': forms.Select(attrs={'placeholder': 'Цель'}),
            'extra': forms.TextInput(attrs={'placeholder': 'Дополнительно'}),
            'start_date': forms.TextInput(attrs={'placeholder': 'Начало'}),
            'position': forms.NumberInput(attrs={'placeholder': 'Позиция в списке'}),
            'description': forms.TextInput(attrs={'placeholder': 'Описание'}),
        }


class ExecutionCardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['execution_id', 'ref_action', 'doc_no', 'doc_date', 'doc_type', 'doc_qty', 'doc_title', 'source_file', 'archive_file']
        widgets = {
            'execution_id': forms.HiddenInput(),
            'ref_action': forms.HiddenInput(),
            'doc_no': forms.TextInput(attrs={'placeholder': 'Номер документа'}),
            'doc_type': forms.Select(attrs={'placeholder': 'Тип документа'}),
            'doc_qty': forms.NumberInput(attrs={'placeholder': 'Количество'}),
            'doc_title': forms.TextInput(attrs={'placeholder': 'Заголовок документа'}),
        }

        doc_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y'
        ),
            input_formats='%d.%m.%Y'
        )
