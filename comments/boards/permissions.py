#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import permissions


class IsOwnerAndPostIsNotOlderThan(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        d = timezone.now() - timedelta(minutes=settings.POSTS_FROZEN_AFTER)
        return obj.creator == request.user and obj.created > d
