#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<pk>[a-zA-Z0-9_\-]{11})/$', views.Votes.as_view()),
]
