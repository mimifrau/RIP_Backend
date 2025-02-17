# Generated by Django 4.2.7 on 2025-01-24 19:57

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
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Телефон')),
                ('description', models.TextField(max_length=500, verbose_name='Описание')),
                ('status', models.IntegerField(choices=[(1, 'Действует'), (2, 'Удалена')], default=1, verbose_name='Статус')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Фото')),
                ('decryption', models.CharField(verbose_name='Расшифровка')),
            ],
            options={
                'verbose_name': 'Код',
                'verbose_name_plural': 'Коды',
                'db_table': 'codes',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Введён'), (2, 'В работе'), (3, 'Завершен'), (4, 'Отклонен'), (5, 'Удален')], default=1, verbose_name='Статус')),
                ('date_created', models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')),
                ('date_formation', models.DateTimeField(blank=True, null=True, verbose_name='Дата формирования')),
                ('date_complete', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')),
                ('name', models.CharField(blank=True, null=True)),
                ('summ', models.IntegerField(blank=True, null=True)),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='moderator', to=settings.AUTH_USER_MODEL, verbose_name='Бухгалтер')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={
                'verbose_name': 'Списание',
                'verbose_name_plural': 'Списания',
                'db_table': 'taxs',
                'ordering': ('-date_formation',),
            },
        ),
        migrations.CreateModel(
            name='CodeTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid', models.IntegerField(default=0, verbose_name='Уплаченная сумма')),
                ('code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.code')),
                ('tax', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.tax')),
            ],
            options={
                'verbose_name': 'м-м',
                'verbose_name_plural': 'м-м',
                'db_table': 'code_tax',
                'ordering': ('pk',),
            },
        ),
        migrations.AddConstraint(
            model_name='codetax',
            constraint=models.UniqueConstraint(fields=('code', 'tax'), name='code_tax_constraint'),
        ),
    ]
