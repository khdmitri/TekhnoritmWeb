# Generated by Django 3.0.3 on 2020-02-04 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='Дата создания')),
                ('avatar', models.ImageField(default='avatar/images/default_avatar.jpg', height_field=60, max_length=200, upload_to='avatar/images/', width_field=60)),
                ('position', models.CharField(choices=[('Делопроизводитель', 'Делопроизводитель'), ('Генеральный_директор', 'Генеральный директор'), ('Руководитель_ОИ', 'Руководитель ОИ'), ('Руководитель_ИЛ', 'Руководитель ИЛ'), ('Инженер_лаборатории', 'Инженер лаборатории'), ('Инженер_инспектор', 'Инженер инспектор')], default='Делопроизводитель', max_length=128)),
                ('is_new', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_view_orders', 'Profile can view ORDERS workflow'), ('can_view_laboratory', 'Profile can view laboratory functions'), ('can_view_inspection', 'Profile can view inspection activities'), ('can_view_stats', 'Profile can view statistics'), ('site_administrator', 'Profile can manage web application')),
            },
        ),
    ]
