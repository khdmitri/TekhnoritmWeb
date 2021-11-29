from django import forms
from .models import ArchiveObject


class ArchiveForm(forms.Form):

    from_date = forms.DateField(widget=forms.DateInput(
        format='%d.%m.%Y',
        attrs={'placeholder': 'Искать с'}
    ),
        input_formats=['%d.%m.%Y',]
    )

    to_date = forms.DateField(widget=forms.DateInput(
        format='%d.%m.%Y',
        attrs={'placeholder': 'Искать до'}
    ),
        input_formats=['%d.%m.%Y',]
    )

    order_context = forms.CharField(max_length=128,
                                    help_text='Поиск по заявочной информации: номер заявки, заявитель, регион',
                                    required=False)
    task_context = forms.CharField(max_length=128,
                                   help_text='Поиск по внутренней информации: подразделение, тип задачи',
                                   required=False)
    execution_context = forms.CharField(max_length=128,
                                        help_text='Поиск внутри подразделения: внутр.исполнитель, внеш.исполнитель, цель',
                                        required=False)
    card_context = forms.CharField(max_length=128,
                                   help_text='Контекст документа: название, номер, заголовок, тип',
                                   required=False)
