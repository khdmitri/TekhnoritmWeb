from django import forms

from export.choices import EXPORT_CHOICES


class ExportProtocolForm(forms.Form):
    action = forms.ChoiceField(choices=EXPORT_CHOICES,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    from_date = forms.DateField(widget=forms.DateInput(
        format='%d.%m.%Y',
        attrs={'placeholder': 'Начальная дата'}
    ),
        input_formats=['%d.%m.%Y',], required=False
    )
    to_date = forms.DateField(widget=forms.DateInput(
        format='%d.%m.%Y',
        attrs={'placeholder': 'Конечная дата', 'class': 'form-control'}
    ),
        input_formats=['%d.%m.%Y',], required=False
    )


class ProtocolAddressFiasForm(forms.Form):
    address = forms.CharField(max_length=1024, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    address_fias = forms.CharField(max_length=4096, widget=forms.HiddenInput())
    protocol_id = forms.IntegerField(widget=forms.HiddenInput())
