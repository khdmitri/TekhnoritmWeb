# Generated by Django 3.0.2 on 2021-02-10 06:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0014_auto_20201001_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_type', models.CharField(choices=[('Договор', 'Договор'), ('Доп. соглашение', 'Доп. соглашение'), ('Заказ', 'Заказ')], default='Договор', max_length=64, verbose_name='Тип контракта')),
                ('comment', models.TextField(blank=True, max_length=512, null=True, verbose_name='Описание')),
                ('scan_file', models.FileField(blank=True, help_text='Прикрепите скан договора/заказа/соглашения...', max_length=200, null=True, upload_to='references/contracts/')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='Дата создания')),
                ('contract_date', models.DateField(blank=True, null=True, verbose_name='Дата договора')),
                ('expired_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('closed_date', models.DateField(blank=True, null=True, verbose_name='Дата закрытия')),
                ('doc_no', models.CharField(blank=True, max_length=128, null=True, verbose_name='Номер договора')),
                ('is_parent', models.BooleanField(default=True, verbose_name='Родительский')),
                ('ref_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='references.Client', verbose_name='Заказчик')),
                ('ref_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='references.Contract')),
            ],
        ),
    ]
