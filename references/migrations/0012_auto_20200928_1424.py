# Generated by Django 3.0.7 on 2020-09-28 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0011_auto_20200826_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaulttasks',
            name='ext_executor',
            field=models.CharField(blank=True, choices=[('RPN', 'Роспотребнадзор'), ('FMBA', 'ФМБА'), ('OWNER', 'Владелец ПРТО'), ('CLIENT', 'Заказчик'), ('OTHER', 'Иное')], max_length=64, null=True, verbose_name='Внешний исполнитель'),
        ),
    ]