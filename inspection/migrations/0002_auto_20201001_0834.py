# Generated by Django 3.0.2 on 2020-10-01 04:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inspection', '0001_initial'),
        ('references', '0013_auto_20201001_0834'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectionobject',
            name='ref_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Order', verbose_name='Заявка'),
        ),
        migrations.AddField(
            model_name='incomedocumentez',
            name='ref_ez',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.EZ', verbose_name='ЭЗ'),
        ),
        migrations.AddField(
            model_name='incomedocument',
            name='ref_see',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.SEE', verbose_name='СЭЭ'),
        ),
        migrations.AddField(
            model_name='ez',
            name='ref_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inspection.InspectionObject', verbose_name='Объект'),
        ),
        migrations.AddField(
            model_name='evalpoints',
            name='ref_see',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.SEE', verbose_name='СЭЭ'),
        ),
        migrations.AddField(
            model_name='documentsign',
            name='ref_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник'),
        ),
        migrations.AddField(
            model_name='commonobjectinfo',
            name='ref_order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.Order'),
        ),
        migrations.AddField(
            model_name='commonobjectinfo',
            name='ref_owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='references.Client', verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='commonobjectinfo',
            name='ref_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project', to='references.Client', verbose_name='Проектант'),
        ),
    ]