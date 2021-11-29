# Generated by Django 2.1.4 on 2020-04-08 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('accounts', '0015_auto_20200408_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='default_perm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Permission', verbose_name='Права по умолчанию'),
        ),
    ]