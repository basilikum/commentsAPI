#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^api-token-auth/', views.obtain_jwt_token),
    url(r'^verify-token/', views.verify_jwt_token),
    url(r'^refresh-token/', views.refresh_jwt_token),
    url(r'^twitter', views.twitter),
    url(r'^google', views.google),
    url(r'^facebook', views.facebook)
]
