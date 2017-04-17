#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import permissions

class IsNotOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator != request.user
