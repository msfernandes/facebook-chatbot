# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-10 04:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lomadee', '0003_auto_20170910_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
