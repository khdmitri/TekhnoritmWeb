from django import forms
from .models import Pribor, ProtocolPribor


class PriborForm(forms.ModelForm):

    class Meta:
        model = Pribor
        fields = [
            'id',
            'name',
            'category',
            'status',
            'purpose',
            'facility_no',
            'reestr_no',
            'inv_no',
            'unique_id',
            'certificate_no',
            'certificate_place',
            'comment',
            'produce_date',
            'certificate_date',
            'expire_date',
            'limit',
            'sensitivity',
            'accuracy'
        ]
        widgets = {
            'id': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'placeholder': 'Наименование'}),
            'category': forms.Select(attrs={'placeholder': 'Категория'}),
            'purpose': forms.TextInput(attrs={'placeholder': 'Назначение прибора'}),
            'facility_no': forms.TextInput(attrs={'placeholder': 'Заводской номер'}),
            'reestr_no': forms.TextInput(attrs={'placeholder': 'Номер в реестре'}),
            'inv_no': forms.TextInput(attrs={'placeholder': 'Инвентарный номер'}),
            'certificate_no': forms.TextInput(attrs={'placeholder': 'Номер свидетельства'}),
            'certificate_place': forms.TextInput(attrs={'placeholder': 'Место поверки'}),
            'comment': forms.TextInput(attrs={'placeholder': 'Примечание'}),
            'limit': forms.TextInput(attrs={'placeholder': 'Диапазон'}),
            'sensitivity': forms.TextInput(attrs={'placeholder': 'Чувствительность'}),
            'accuracy': forms.TextInput(attrs={'placeholder': 'Погрешность'}),
        }

        produce_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата выпуска'}
        ),
            input_formats='%d.%m.%Y'
        )

        certificate_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата поверки'}
        ),
            input_formats='%d.%m.%Y'
        )

        expire_date = forms.DateField(widget=forms.DateInput(
            format='%d.%m.%Y',
            attrs={'placeholder': 'Дата очередной поверки'}
        ),
            input_formats='%d.%m.%Y'
        )
