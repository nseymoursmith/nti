# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_auto_20160316_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerorder',
            name='completion_date',
            field=models.DateField(blank=True, verbose_name=b'Completion Date'),
        ),
        migrations.AlterField(
            model_name='productrequirement',
            name='completion_date',
            field=models.DateField(blank=True, verbose_name=b'Completion Date'),
        ),
    ]
