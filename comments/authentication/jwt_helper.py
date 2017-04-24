#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from calendar import timegm

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from rest_framework.authentication import get_authorization_header

import jwt

User = get_user_model()


def get_token_from_request(request):
    auth = get_authorization_header(request).split()
    auth_header_prefix = settings.JWT_AUTH_HEADER_PREFIX.lower()
    if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
        return None
    if len(auth) == 1 or len(auth) > 2:
        return ""
    return auth[1]


def jwt_decode(token):
    return jwt.decode(
        token,
        settings.JWT_PUBLIC_KEY or settings.JWT_SECRET_KEY or settings.SECRET_KEY,
        settings.JWT_VERIFY,
        options={
            'verify_exp': settings.JWT_VERIFY_EXPIRATION,
        },
        leeway=settings.JWT_LEEWAY,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        algorithms=[settings.JWT_ALGORITHM]
    )


def jwt_encode(payload):
    return jwt.encode(
        payload,
        settings.JWT_PRIVATE_KEY or settings.JWT_SECRET_KEY or settings.SECRET_KEY,
        settings.JWT_ALGORITHM
    ).decode('utf-8')


def verify_token(token):
    payload = get_token_payload(token)
    return payload and check_user(payload) is not None


def get_token_payload(token):
    try:
        payload = jwt_decode(token)
    except (jwt.ExpiredSignature, jwt.DecodeError, jwt.InvalidTokenError):
        return None
    return payload


def refresh_token(token):
    try:
        payload = jwt_decode(token)
    except (jwt.ExpiredSignature, jwt.DecodeError, jwt.InvalidTokenError):
        return None
    user = check_user(payload)
    if user is None:
        return None
    orig_iat = payload.get('orig_iat')
    if not orig_iat:
        return None
    refresh_limit = settings.JWT_REFRESH_EXPIRATION_DELTA
    expiration_timestamp = orig_iat + int(refresh_limit)
    now_timestamp = get_now_timestamp()
    if now_timestamp > expiration_timestamp:
        return None
    new_payload = get_payload(user)
    new_payload['orig_iat'] = orig_iat
    return jwt_encode(new_payload)


def check_user(payload):
    username = payload.get('username')
    if not username:
        return None
    try:
        user = User.objects.get_by_natural_key(username)
    except User.DoesNotExist:
        return None
    if not user.is_active:
        return None
    if not set(get_permissions(user)) == set(payload.get('permissions')):
        return None
    return user


def get_permissions(user):
    permissions = []
    for p in user.get_all_permissions():
        parts = p.split('.')
        if parts[0] in settings.PERM_CATEGORIES:
            permissions.append(parts[-1])
    return permissions


def get_payload(user):
    payload = {
        'email': user.email,
        'display_name': user.display_name,
        'username': user.username,
        'user_id': user.id,
        'permissions': get_permissions(user),
        'is_active': user.is_active,
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }
    if settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = get_now_timestamp()
    if settings.JWT_AUDIENCE is not None:
        payload['aud'] = settings.JWT_AUDIENCE
    if settings.JWT_ISSUER is not None:
        payload['iss'] = settings.JWT_ISSUER
    return payload


def get_now_timestamp():
    return timegm(datetime.utcnow().utctimetuple())
