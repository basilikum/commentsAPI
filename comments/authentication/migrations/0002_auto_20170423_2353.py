# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-23 21:53
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmuser',
            name='display_name',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='cmuser',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cmuser',
            name='username',
            field=models.CharField(max_length=32, unique=True, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
    ]