# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 15:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0026_additionalitem_added'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assembler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('website', models.URLField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AssemblyOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name=b'Date sent')),
                ('due_date', models.DateField(default=datetime.date.today, verbose_name=b'Due date')),
                ('completed', models.BooleanField(default=False, verbose_name=b'Completed?')),
                ('assembler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Assembler')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAssembly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_ordered', models.IntegerField(default=1)),
                ('completion_date', models.DateField(default=datetime.date.today, verbose_name=b'Completion Date')),
                ('completed', models.BooleanField(default=False, verbose_name=b'Completed?')),
                ('assembly_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.AssemblyOrder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Product')),
            ],
        ),
        migrations.AlterField(
            model_name='additionalitem',
            name='number_ordered',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='customerorder',
            name='completion_date',
            field=models.DateField(default=datetime.date.today, verbose_name=b'Completion Date'),
        ),
        migrations.AlterField(
            model_name='productrequirement',
            name='completion_date',
            field=models.DateField(default=datetime.date.today, verbose_name=b'Completion Date'),
        ),
        migrations.AlterField(
            model_name='productrequirement',
            name='number_ordered',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='assemblyorder',
            name='product',
            field=models.ManyToManyField(through='inventory.ProductAssembly', to='inventory.Product'),
        ),
    ]
