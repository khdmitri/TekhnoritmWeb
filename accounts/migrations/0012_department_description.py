# Generated by Django 3.0.2 on 2020-02-06 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20200206_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='description',
            field=models.TextField(max_length=1024, null=True, verbose_name='Описание'),
        ),
    ]