#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^register', views.UserCreate.as_view()),
    url(r'^finalize', views.UserFinalize.as_view()),
    url(r'^user-exists', views.UserExists.as_view()),
    url(r'^(?P<uid>[a-zA-Z0-9_\-]{11})$', views.UserDetail.as_view()),
    url(r'^(?P<uid>[a-zA-Z0-9_\-]{11})/avatar', views.UserAvatar.as_view()),
]

