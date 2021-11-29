# Generated by Django 3.0.3 on 2020-02-04 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20200204_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='position',
            field=models.CharField(choices=[('Не_определено', 'Нет должности'), ('Делопроизводитель', 'Делопроизводитель'), ('Генеральный_директор', 'Генеральный директор'), ('Руководитель_ОИ', 'Руководитель ОИ'), ('Руководитель_ИЛ', 'Руководитель ИЛ'), ('Инженер_лаборатории', 'Инженер лаборатории'), ('Инженер_инспектор', 'Инженер инспектор')], default='Нет должности', max_length=128),
        ),
    ]