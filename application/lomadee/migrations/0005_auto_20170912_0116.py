# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-12 04:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lomadee', '0004_auto_20170910_0115'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='computer',
            options={'ordering': ['-rating'], 'verbose_name': 'Computer', 'verbose_name_plural': 'Computers'},
        ),
    ]
