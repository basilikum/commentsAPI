#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from .jwt_helper import get_token_from_request, check_user, get_token_payload


class JWTAuthentication(BaseAuthentication):

    www_authenticate_realm = 'api'

    def authenticate(self, request):
        token = get_token_from_request(request)
        if token is None:
            return None
        payload = get_token_payload(token)
        if not payload:
            raise exceptions.AuthenticationFailed('Authentication failed.')
        user = check_user(payload)
        if user is None:
            raise exceptions.AuthenticationFailed('Authentication failed.')
        return (user, token)

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)
