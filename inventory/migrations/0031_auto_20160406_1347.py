# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-06 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0030_customerorder_tracking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerorder',
            name='tracking',
            field=models.URLField(blank=True, max_length=300, verbose_name=b'Tracking URL:'),
        ),
    ]
