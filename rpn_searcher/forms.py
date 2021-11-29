from django import forms


class UploadFilesForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                 help_text='Загрузите файлы (можно загружить несколько файлов сразу)')
