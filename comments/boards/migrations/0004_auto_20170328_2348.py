# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-28 21:48
from __future__ import unicode_literals

import boards.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0003_auto_20170327_1712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='positive',
        ),
        migrations.AddField(
            model_name='vote',
            name='value',
            field=models.IntegerField(default=1, validators=[boards.validators.validate_vote_value]),
            preserve_default=False,
        ),
    ]
