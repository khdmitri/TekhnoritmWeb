# Generated by Django 3.0.2 on 2020-04-05 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0002_prtotype'),
    ]

    operations = [
        migrations.AddField(
            model_name='prtotype',
            name='order',
            field=models.IntegerField(default=1, verbose_name='Порядок'),
        ),
    ]
