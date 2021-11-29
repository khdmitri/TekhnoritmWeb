# Generated by Django 3.0.3 on 2020-02-04 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile_is_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='position',
            field=models.CharField(choices=[('Делопроизводитель', 'Делопроизводитель'), ('Генеральный_директор', 'Генеральный директор'), ('Руководитель_ОИ', 'Руководитель ОИ'), ('Руководитель_ИЛ', 'Руководитель ИЛ'), ('Инженер_лаборатории', 'Инженер лаборатории'), ('Инженер_инспектор', 'Инженер инспектор')], default='Делопроизводитель', max_length=128),
        ),
    ]