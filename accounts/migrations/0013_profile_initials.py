# Generated by Django 3.0.2 on 2020-04-05 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_department_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='initials',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
