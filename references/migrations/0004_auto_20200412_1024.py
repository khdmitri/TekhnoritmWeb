# Generated by Django 3.0.2 on 2020-04-12 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0003_prtotype_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unibook2',
            name='item_long',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Запись'),
        ),
    ]
