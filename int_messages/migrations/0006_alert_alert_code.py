# Generated by Django 3.0.7 on 2020-09-28 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('int_messages', '0005_auto_20200223_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='alert_code',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Код оповещения'),
        ),
    ]
