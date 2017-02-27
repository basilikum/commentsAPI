#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models


class Site(models.Model):
    id = models.CharField(max_length=7, primary_key=True)
    url = models.URLField(max_length=100, unique=True, db_index=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True, related_name='sites')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.url


class QueryRule(models.Model):
    site = models.ForeignKey(Site, models.CASCADE, related_name='query_rules')
    path = models.CharField(max_length=100)
    param = models.CharField(max_length=50)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True, related_name='query_rules')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{}{}?{}='.format(self.site.url, self.path, self.param)


class Board(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    title = models.CharField(max_length=200)
    site = models.ForeignKey(Site, models.CASCADE, related_name='boards')
    path = models.CharField(max_length=200)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True, related_name='boards')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{}'.format(self.title)


class BoardGroup(models.Model):
    boards = models.ManyToManyField(Board)

    def __unicode__(self):
        return '{}'.format(self.title)


class Thread(models.Model):
    id = models.CharField(max_length=11, primary_key=True)
    board = models.ForeignKey(Board, models.CASCADE, related_name='threads')
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True, related_name='threads')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    op = models.OneToOneField('Post', models.CASCADE, related_name='own_thread')

    def __unicode__(self):
        return '{}'.format(self.title)


class Post(models.Model):
    id = models.CharField(max_length=11, primary_key=True)
    thread = models.ForeignKey(Thread, models.CASCADE, related_name='posts')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True, related_name='posts')
    origin = models.ForeignKey(Site, models.CASCADE, related_name='posts')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('Post', models.CASCADE, null=True, blank=True, related_name='children')
    text = models.TextField()

    def __unicode__(self):
        return '{}'.format(self.title)
