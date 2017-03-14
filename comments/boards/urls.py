#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.BoardList.as_view()),
    url(r'^(?P<pk>[a-zA-Z0-9_\-]{8})/$', views.BoardDetail.as_view()),
    url(r'^url/$', views.BoardByUrl.as_view()),
    url(r'^threads/$', views.ThreadListCreate.as_view()),
    url(r'^threads/(?P<pk>[a-zA-Z0-9_\-]{11})/$', views.ThreadDetail.as_view()),
    url(r'^posts/$', views.PostListCreate.as_view()),
    url(r'^posts/(?P<pk>[a-zA-Z0-9_\-]{11})/$', views.PostDetail.as_view())
]
