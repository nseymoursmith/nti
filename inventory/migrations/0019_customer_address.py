# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-01 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_auto_20160301_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='address',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]