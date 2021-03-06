# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-07 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0010_auto_20170430_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='qs_rules',
            field=models.ManyToManyField(blank=True, related_name='sites', to='boards.QsRule'),
        ),
        migrations.AlterField(
            model_name='site',
            name='re_rules',
            field=models.ManyToManyField(blank=True, related_name='sites', to='boards.ReRule'),
        ),
    ]
