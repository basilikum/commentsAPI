#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from rest_framework import permissions

class HasValidRecaptchaResponse(permissions.BasePermission):
    def has_permission(self, request, view):
        captcha_response = request.data.get('g-recaptcha-response', None)
        if not captcha_response:
            return False
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': '6LcvUh4UAAAAACIgexKN2HZopsmkbIBtkynG8SnJ',
            'response': captcha_response
        })
        if r.status_code != 200:
            return False
        return r.json()['success']
