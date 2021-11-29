from django import forms
from order_control.models import ControlConfig
from .choices import ALERT_TYPES, EXECUTOR_TYPES, SEARCH_TYPES


class ControlConfigForm(forms.ModelForm):
    class Meta:
        model = ControlConfig
        fields = ['ref_task', 'is_warn_control', 'is_dang_control', 'warn_days', 'dang_days', 'is_warn_alert',
                  'is_dang_alert', 'warn_alert_type', 'dang_alert_type']
        widgets = {
            'warn_alert_type': forms.RadioSelect(choices=ALERT_TYPES),
            'dang_alert_type': forms.RadioSelect(choices=ALERT_TYPES),
            'ref_task': forms.HiddenInput(),
        }
        labels = {
            'is_warn_control': 'Включить контроль',
            'is_dang_control': 'Включить контроль',
            'warn_days': 'Дней спустя',
            'dang_days': 'Дней спустя',
            'is_warn_alert': 'Включить оповещение',
            'is_dang_alert': 'Включить оповещение',
            'warn_alert_type': 'Тип оповещения',
            'dang_alert_type': 'Тип оповещения',
        }


class StandardRequestForm(forms.Form):
    use_region = forms.BooleanField(label='Учесть регион', required=False)
    region = forms.CharField(label='', required=False)
    target = forms.CharField(label='Цель', required=False)
    search_text = forms.CharField(label='Поисковый запрос', required=False)
    type_search = forms.CharField(label='Тип поиска', required=False)
    only_warning = forms.BooleanField(label='Только горящие', required=False)
    executor = forms.IntegerField(required=False)
    int_executor = forms.CharField(max_length=256, required=False)
    ext_executor = forms.CharField(max_length=256, required=False)

    widgets = {
        'region': forms.Select(attrs={'placeholder': 'Выберите регион...'}),
        'target': forms.Select(),
        'executor': forms.Select(choices=EXECUTOR_TYPES),
        'type_search': forms.RadioSelect(choices=SEARCH_TYPES),
    }
