# Generated by Django 3.0.2 on 2020-04-28 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0004_auto_20200412_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='request_sign_person',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Заявления подписывает'),
        ),
        migrations.AddField(
            model_name='client',
            name='request_sign_position',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Должность подписанта'),
        ),
        migrations.AddField(
            model_name='client',
            name='request_template',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Шаблон'),
        ),
    ]
