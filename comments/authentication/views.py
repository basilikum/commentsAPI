#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .jwt_helper import (
    jwt_encode,
    get_payload,
    verify_token,
    refresh_token
)


@api_view(['POST'], exclude_from_schema=True)
@authentication_classes([])
@permission_classes([])
def obtain_jwt_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"message": "could not authenticate"}, status=401)
    if not user.is_active:
        return JsonResponse({"message": "the user is not active"}, status=401)
    print user.get_all_permissions()
    payload = get_payload(user)
    token = jwt_encode(payload)
    return JsonResponse({'token': token})


@api_view(['POST'], exclude_from_schema=True)
@authentication_classes([])
@permission_classes([])
def verify_jwt_token(request):
    token = request.data.get('token')
    return JsonResponse({'verified': verify_token(token)})


@api_view(['POST'], exclude_from_schema=True)
@authentication_classes([])
@permission_classes([])
def refresh_jwt_token(request):
    token = request.data.get('token')
    new_token = refresh_token(token)
    if not new_token:
        return JsonResponse({"message": "token can't be refreshed"}, status=401)
    return JsonResponse({'token': new_token})
