#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from django.conf import settings
from django.db import models

from common.models import random_id


def generate_site_id():
    return random_id(Site, 7)

def generate_board_id():
    return random_id(Board, 8)

def generate_thread_id():
    return random_id(Thread, 11)

def generate_post_id():
    return random_id(Post, 11)


class Site(models.Model):
    id = models.CharField(max_length=7, primary_key=True, default=generate_site_id)
    netloc = models.URLField(max_length=100, unique=True, db_index=True)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='sites'
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.netloc


class ReRule(models.Model):
    site = models.ForeignKey(Site, models.CASCADE, related_name='re_rules')
    regex = models.CharField(max_length=500)
    repl = models.CharField(max_length=500)

    def apply(self, path):
        return re.sub(self.regex, self.repl, path)

    def __unicode__(self):
        return '{} ({} => {})'.format(
            self.site.netloc,
            self.regex,
            self.repl
        )


class QsRule(models.Model):
    site = models.ForeignKey(Site, models.CASCADE, related_name='qs_rules')
    path = models.CharField(max_length=2000)
    params = models.CharField(max_length=500)

    def get_params(self):
        return self.params.split('&')

    def set_params(self, value):
        params = [str(p) for p in value]
        params.sort()
        self.params = '&'.join(params)

    def apply(self, params):
        parts = []
        param_names = self.get_params()
        for param_name in param_names:
            if param_name not in params:
                continue
            parts.append('{}={}'.format(param_name, params[param_name][0]))
        if len(parts) == 0:
            return ''
        return '?' + '&'.join(parts)

    class Meta:
        unique_together = ('site', 'path')
        index_together = ['site', 'path']

    def __unicode__(self):
        return '{}{}?{}'.format(
            self.site.netloc,
            self.path,
            self.params
        )


class Board(models.Model):
    id = models.CharField(max_length=8, primary_key=True, default=generate_board_id)
    title = models.CharField(max_length=2000)
    site = models.ForeignKey(Site, models.CASCADE, related_name='boards')
    path = models.CharField(max_length=2000)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='boards'
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('site', 'path')
        index_together = ['site', 'path']

    def __unicode__(self):
        return '{}'.format(self.title)


class BoardGroup(models.Model):
    boards = models.ManyToManyField(Board)

    def __unicode__(self):
        return '{}'.format(self.title)


class Thread(models.Model):
    id = models.CharField(max_length=11, primary_key=True, default=generate_thread_id)
    board = models.ForeignKey(Board, models.CASCADE, related_name='threads')
    raw_path = models.CharField(max_length=2000)
    title = models.CharField(max_length=100)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='threads'
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{}'.format(self.title)


class Post(models.Model):
    id = models.CharField(max_length=11, primary_key=True, default=generate_post_id)
    thread = models.ForeignKey(Thread, models.CASCADE, related_name='posts')
    origin = models.ForeignKey(
        'Post', models.CASCADE,
        null=True, blank=True, related_name='replies'
    )
    parent = models.ForeignKey(
        'Post', models.CASCADE,
        null=True, blank=True, related_name='children'
    )
    text = models.TextField(max_length=65536)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='posts'
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    site = models.ForeignKey(Site, models.CASCADE, related_name='posts')

    def __unicode__(self):
        return '{}'.format(self.thread.title)


class Vote(models.Model):
    post = models.ForeignKey(Post, models.CASCADE, related_name='votes')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL,
        null=True, blank=True, related_name='votes'
    )
    positive = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'creator')
        index_together = ['post', 'creator']

    def __unicode__(self):
        v = '+1' if self.positive else '-1'
        return u'{} by {} on {}'.format(v, self.creator.display_name, self.post_id)
