# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-06 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0031_auto_20160406_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='productrequirement',
            name='self_built',
            field=models.BooleanField(default=False),
        ),
    ]
