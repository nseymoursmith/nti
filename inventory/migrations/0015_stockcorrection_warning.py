# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_auto_20160224_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockcorrection',
            name='warning',
            field=models.CharField(default=b"Warning: this can only be applied once. Changing values after creation will have no effect - don't do it!", max_length=256),
        ),
    ]
