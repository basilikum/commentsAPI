#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models

from common.models import random_id

from .validators import validate_vote_value


def generate_vote_entity_id():
    return random_id(VoteEntity, 11)


class VoteEntity(models.Model):
    id = models.CharField(max_length=11, primary_key=True, default=generate_vote_entity_id)
    total = models.IntegerField(default=0)
    plus = models.IntegerField(default=0)
    minus = models.IntegerField(default=0)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='vote_entities'
    )

    def update(self):
        votes = list([v for v in self.votes.all()])
        self.plus = len([v for v in votes if v.value == 1])
        self.minus = len([v for v in votes if v.value == -1])
        self.total = self.plus - self.minus
        self.save()

    def __unicode__(self):
        return '{}: {} / {}'.format(self.id, self.plus, self.minus)


class Vote(models.Model):
    vote_entity = models.ForeignKey(VoteEntity, models.CASCADE, related_name='votes')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='votes'
    )
    value = models.IntegerField(validators=[validate_vote_value])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vote_entity', 'creator')
        index_together = ['vote_entity', 'creator']

    def __unicode__(self):
        v = '+1' if self.value == 1 else '-1'
        return u'{} by {} on {}'.format(v, self.creator.display_name, self.vote_entity_id)
