# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-10 19:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import votes.models
import votes.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(validators=[votes.validators.validate_vote_value])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='votes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VoteEntity',
            fields=[
                ('id', models.CharField(default=votes.models.generate_vote_entity_id, max_length=11, primary_key=True, serialize=False)),
                ('total', models.IntegerField(default=0)),
                ('plus', models.IntegerField(default=0)),
                ('minus', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='vote_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='votes.VoteEntity'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('vote_entity', 'creator')]),
        ),
        migrations.AlterIndexTogether(
            name='vote',
            index_together=set([('vote_entity', 'creator')]),
        ),
    ]
