# Generated by Django 2.1 on 2019-08-26 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unicorn', '0003_abstractunit_standard_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abstractunit',
            name='standard_size',
        ),
        migrations.AddField(
            model_name='abstractunit',
            name='status',
            field=models.SmallIntegerField(choices=[(0, ''), (1, 'Metric'), (2, 'Standard')], default=0, verbose_name='Status'),
        ),
    ]
