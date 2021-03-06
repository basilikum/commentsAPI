# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 14:30
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import F


def update_vote_entity(vote_entity):
    votes = list([v for v in vote_entity.votes.all()])
    vote_entity.plus = len([v for v in votes if v.value == 1])
    vote_entity.minus = len([v for v in votes if v.value == -1])
    vote_entity.total = vote_entity.plus - vote_entity.minus
    vote_entity.save()


def set_creator(apps, schema_editor):
    Post = apps.get_model('boards', 'Post')
    Vote = apps.get_model('votes', 'Vote')
    VoteEntity = apps.get_model('votes', 'VoteEntity')
    for post in Post.objects.all():
        post.vote_entity.creator = post.creator
        post.vote_entity.save()
    Vote.objects.filter(vote_entity__creator=F('creator')).delete()
    for ve in VoteEntity.objects.all():
        update_vote_entity(ve)


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0002_voteentity_creator'),
    ]

    operations = [
        migrations.RunPython(set_creator, do_nothing),
    ]
