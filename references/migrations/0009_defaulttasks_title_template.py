# Generated by Django 3.0.2 on 2020-08-25 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0008_defaulttasks_fill_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaulttasks',
            name='title_template',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Шаблон заголовка (!#)'),
        ),
    ]