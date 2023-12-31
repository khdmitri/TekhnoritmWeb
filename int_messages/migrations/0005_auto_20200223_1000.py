# Generated by Django 3.0.2 on 2020-02-23 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('int_messages', '0004_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='action_url',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Ссылка на действие'),
        ),
        migrations.AddField(
            model_name='alert',
            name='code',
            field=models.IntegerField(default=0, verbose_name='Код сообщения'),
            preserve_default=False,
        ),
    ]
