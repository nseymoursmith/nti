# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 13:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20160224_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.Customer'),
        ),
    ]
