# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter


admin.autodiscover()
router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('authentication.urls')),
    url(r'^boards/', include('boards.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^votes/', include('votes.urls')),
]
