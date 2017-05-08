#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from django.conf import settings

from rest_framework import permissions

class HasValidRecaptchaResponse(permissions.BasePermission):
    def has_permission(self, request, view):
        captcha_response = request.data.get('g-recaptcha-response', None)
        if not captcha_response:
            return False
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': settings.RECAPTCHA_SECRET,
            'response': captcha_response
        })
        if r.status_code != 200:
            return False
        return r.json()['success']


class IsActiveOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_active
