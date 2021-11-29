from django import forms
from .models import Generator


class GeneratorForm(forms.ModelForm):
    class Meta:
        model = Generator
        fields = ['use_area', 'no', 'gen_type', 'year']
