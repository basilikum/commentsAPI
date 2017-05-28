#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^register', views.UserCreate.as_view()),
    url(r'^finalize', views.UserFinalize.as_view()),
    url(r'^user-exists', views.UserExists.as_view()),
    url(r'^avatar$', views.UserAvatarManage.as_view()),
    url(r'^avatar/(?P<img_id>[a-zA-Z0-9_\-]{5}).jpg$', views.UserImage.as_view()),
    url(r'^(?P<uid>[a-zA-Z0-9_\-]{11})$', views.UserDetail.as_view()),
    url(r'^(?P<uid>[a-zA-Z0-9_\-]{11})/avatar.jpg$', views.UserAvatar.as_view()),
]

