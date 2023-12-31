# Generated by Django 3.0.2 on 2020-03-28 05:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0012_department_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=256, verbose_name='Краткое наименование')),
                ('long_name', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Полное наименование')),
                ('address_1', models.TextField(blank=True, max_length=512, null=True, verbose_name='Юридический адрес')),
                ('address_2', models.TextField(blank=True, max_length=512, null=True, verbose_name='Физический адрес')),
                ('inn', models.CharField(blank=True, max_length=64, null=True, verbose_name='ИНН')),
                ('ogrn', models.CharField(blank=True, max_length=64, null=True, verbose_name='ОГРН')),
                ('representative', models.CharField(blank=True, max_length=512, null=True, verbose_name='Представитель')),
                ('phone', models.CharField(blank=True, max_length=128, null=True, verbose_name='Тел. номер')),
                ('email', models.CharField(blank=True, max_length=256, null=True, verbose_name='E-mail')),
                ('logo', models.ImageField(default='logo/images/default_logo.jpg', help_text='Загрузите логотип клиента, если доступно', max_length=200, upload_to='logo/images/', verbose_name='Логотип')),
                ('is_owner', models.BooleanField(default=False, help_text='Если отмечено, клиент является и владельцем объектов', verbose_name='Является ли владельцем объектов')),
                ('is_project', models.BooleanField(default=True, help_text='Если отмечено, клиент является проектантом', verbose_name='Является ли проектантом')),
            ],
        ),
        migrations.CreateModel(
            name='UniBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=128, verbose_name='Категория')),
                ('item', models.CharField(blank=True, max_length=256, null=True, verbose_name='Запись')),
            ],
        ),
        migrations.CreateModel(
            name='UniBook2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=128, verbose_name='Категория')),
                ('item_short', models.CharField(blank=True, max_length=256, null=True, verbose_name='Запись')),
                ('item_long', models.CharField(blank=True, max_length=512, null=True, verbose_name='Запись')),
            ],
        ),
        migrations.CreateModel(
            name='DefaultTasks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(choices=[('R1', 'Работы по схеме Р1'), ('R2', 'Работы по схеме Р2'), ('PK-PRTO', 'Производственный контроль (ПРТО)'), ('PK', 'Производственный контроль (лаборатория)'), ('SOUT', 'СОУТ'), ('DOCS', 'Вручение пакета документов/Оплата'), ('OTHER', 'Иное')], max_length=64, verbose_name='Тип задачи')),
                ('ext_executor', models.CharField(blank=True, choices=[('RPN', 'Роспотребнадзор'), ('FMBA', 'ФМБА'), ('OWNER', 'Владелец ПРТО'), ('СLIENT', 'Заказчик'), ('OTHER', 'Иное')], max_length=64, null=True, verbose_name='Внешний исполнитель')),
                ('target', models.CharField(choices=[('OOS', 'Расчет СЗЗ и ЗОЗ'), ('SEE', 'Санитарно-эпидемиологическая экспертиза (Р1)'), ('SEZ', 'Санитарно-эпидемиологическое заключение (Р1-РПН)'), ('PROTOCOL', 'Протокол измерений ЭМП (Р2)'), ('EZ-R2', 'Экспертное заключние по измерениям (Р2)'), ('LETTER', 'Письмо-согласование (Р2-РПН)'), ('DOCS', 'Вручение пакета документов/Оплата'), ('OTHER', 'Иное')], max_length=64, null=True, verbose_name='Целевой документ')),
                ('start_date', models.CharField(blank=True, choices=[('now', 'Текущая дата'), ('none', 'Оставить пустым')], max_length=64, null=True, verbose_name='Начало исполнения')),
                ('position', models.IntegerField(verbose_name='Позиция в списке')),
                ('int_executor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Department', verbose_name='Внутр. исполнитель')),
            ],
        ),
    ]
