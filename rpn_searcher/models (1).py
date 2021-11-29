from django.db import models


class RPNLetter(models.Model):
    attach = models.FileField(upload_to='rpn_searcher/letters/',
                              max_length=200,
                              blank=True,
                              null=True,
                              help_text='Word-файл (письмо-согласование)')
    upload_date = models.DateField(verbose_name='Дата загрузки', auto_now_add=True, auto_now=False)
    orig_file_name = models.CharField(max_length=512, null=True, blank=True)
    text_content = models.CharField(max_length=16384, null=True, blank=True)
    file_create_date = models.DateField(verbose_name='Дата создания файла', null=True, blank=True)
