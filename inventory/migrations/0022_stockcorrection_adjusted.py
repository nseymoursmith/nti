# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 16:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0021_auto_20160309_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockcorrection',
            name='adjusted',
            field=models.BooleanField(default=False),
        ),
    ]
