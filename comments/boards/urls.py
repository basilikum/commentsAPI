#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

# boards
urlpatterns = [
    url(r'^$', views.BoardListCreate.as_view()), #GET: ?url=; CREATE
    url(r'^(?P<pk>[a-zA-Z0-9_\-]{8})/$', views.BoardDetail.as_view()),
]

# threads
urlpatterns = [
    url(r'^$', views.ThreadListCreate.as_view()), #GET: ?boards=1,4,6,7,6,4; CREATE
    url(r'^(?P<pk>[a-zA-Z0-9_\-]{11})/$', views.ThreadDetail.as_view()),
    url(r'^(?P<pk>[a-zA-Z0-9_\-]{11})/posts$', views.PostListCreate.as_view()),
]

# posts
urlpatterns = [
    url(r'^$', views.DocumentUpload.as_view()), #GET: ?boards=1,4,6,7,6,4; CREATE
    url(r'^(?P<pk>[a-zA-Z0-9_\-]{11})/$', views.NodeList.as_view()),
]
