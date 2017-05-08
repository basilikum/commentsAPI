#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
from urlparse import parse_qsl

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse

import requests
from requests_oauthlib import OAuth1

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import HasValidRecaptchaResponse

from .jwt_helper import (
    jwt_encode,
    get_payload,
    verify_token,
    refresh_token
)

from .serializers import (
    UserSerializer,
    UserCreateSocialSerializer,
    UserCreateLocalSerializer,
    UserFinalizeLocalSerializer
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


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def twitter(request):
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    user_url = 'https://api.twitter.com/1.1/users/show.json'
    User = get_user_model()
    if request.data.get('oauth_token') and request.data.get('oauth_verifier'):
        auth = OAuth1(
            settings.TWITTER_CONSUMER_KEY,
            client_secret=settings.TWITTER_CONSUMER_SECRET,
            resource_owner_key=request.data.get('oauth_token'),
            verifier=request.data.get('oauth_verifier')
        )
        r = requests.post(access_token_url, auth=auth)
        profile = dict(parse_qsl(r.text))

        r = requests.get(user_url, auth=auth)
        print r.text

        try:
            user = User.objects.get(twitter=profile['user_id'])
        except User.DoesNotExist:
            serializer = UserCreateSocialSerializer(data={
                'username': profile['screen_name'],
                'ext_picture_url': '',
                'soc_id': profile['user_id'],
                'soc_provider': 'twitter'
            })
            serializer.is_valid()
            user = serializer.save()
        payload = get_payload(user)
        token = jwt_encode(payload)
        return JsonResponse({'token': token})
    else:
        redirect_uri = request.data.get('redirectUri')
        if redirect_uri not in settings.ALLOWED_REDIRECT_URI:
            redirect_uri = settings.REDIRECT_URI
        oauth = OAuth1(
            settings.TWITTER_CONSUMER_KEY,
            client_secret=settings.TWITTER_CONSUMER_SECRET,
            callback_uri=redirect_uri
        )
        r = requests.post(request_token_url, auth=oauth)
        oauth_token = dict(parse_qsl(r.text))
        return JsonResponse(oauth_token)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def google(request):
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    people_api_url = 'https://www.googleapis.com/plus/v1/people/me/openIdConnect'
    User = get_user_model()
    payload = {
        'client_id': request.data.get('clientId'),
        'redirect_uri': request.data.get('redirectUri'),
        'client_secret': settings.GOOGLE_SECRET,
        'code': request.data.get('code'),
        'grant_type': 'authorization_code'
    }

    r = requests.post(access_token_url, data=payload)
    token = r.json()
    headers = {'Authorization': 'Bearer {0}'.format(token['access_token'])}

    r = requests.get(people_api_url, headers=headers)
    profile = r.json()
    picture_url = re.sub(r'sz=[0-9]+$', 'sz=64', profile.get('picture', ''))
    try:
        user = User.objects.get(google=profile['sub'])
    except User.DoesNotExist:
        serializer = UserCreateSocialSerializer(data={
            'username': profile['name'],
            'ext_picture_url': picture_url,
            'soc_id': profile['sub'],
            'soc_provider': 'google'
        })
        serializer.is_valid()
        user = serializer.save()
    payload = get_payload(user)
    token = jwt_encode(payload)
    return JsonResponse({'token': token})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def facebook(request):
    access_token_url = 'https://graph.facebook.com/v2.3/oauth/access_token'
    graph_api_url = 'https://graph.facebook.com/v2.9'
    User = get_user_model()
    params = {
        'client_id': request.data.get('clientId'),
        'redirect_uri': request.data.get('redirectUri'),
        'client_secret': settings.FACEBOOK_SECRET,
        'code': request.data.get('code')
    }

    r = requests.get(access_token_url, params=params)
    access_token = json.loads(r.text)

    r = requests.get(graph_api_url + '/me', params=access_token)
    profile = json.loads(r.text)

    picture_params = {
        'width': 64,
        'format': 'json',
        'redirect': 'false'
    }
    picture_url = '{}/{}/picture'.format(graph_api_url, profile['id'])
    r = requests.get(picture_url, params=picture_params)
    picture_url = r.json()['data']['url']

    try:
        user = User.objects.get(facebook=profile['id'])
    except User.DoesNotExist:
        serializer = UserCreateSocialSerializer(data={
            'username': profile['name'],
            'ext_picture_url': picture_url,
            'soc_id': profile['id'],
            'soc_provider': 'facebook'
        })
        serializer.is_valid()
        user = serializer.save()
    payload = get_payload(user)
    token = jwt_encode(payload)
    return JsonResponse({'token': token})


class UserExists(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        username = request.query_params.get('username')
        User = get_user_model()
        return Response({'exists': User.objects.filter(username=username).exists()})


class UserCreate(CreateAPIView):
    permission_classes = (HasValidRecaptchaResponse,)
    serializer_class = UserCreateLocalSerializer


class UserFinalize(UpdateAPIView):
    permission_classes = (IsAuthenticated, HasValidRecaptchaResponse)
    serializer_class = UserFinalizeLocalSerializer

    def get_object(self):
        return self.request.user


class UserDetail(RetrieveAPIView):
    permission_classes = ()
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
