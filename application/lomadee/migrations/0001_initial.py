# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-07 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('thumbnail_url', models.URLField()),
                ('cpu', models.CharField(choices=[('i3', 'Intel Core i3'), ('i5', 'Intel Core i5'), ('i7', 'Intel Core i7')], max_length=2)),
                ('gpu', models.BooleanField(default=False)),
                ('ssd', models.BooleanField(default=False)),
                ('ram', models.IntegerField(default=2)),
                ('disk', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Computer',
                'verbose_name_plural': 'Computers',
            },
        ),
    ]
