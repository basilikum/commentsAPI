# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 14:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('votes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voteentity',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vote_entities', to=settings.AUTH_USER_MODEL),
        ),
    ]
