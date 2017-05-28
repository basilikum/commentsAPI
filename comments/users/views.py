#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from common.permissions import HasValidRecaptchaResponse
from common.renderer import JPGRenderer

from .serializers import (
    UserSerializer,
    UserCreateLocalSerializer,
    UserFinalizeLocalSerializer,
    UserImageSerializer,
    UserAvatarSerializer,
    UserAvatarUpdateSerializer,
    UserAvatarUploadSerializer
)


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
    lookup_field = 'uid'


class UserAvatar(APIView):
    permission_classes = ()
    renderer_classes = (JPGRenderer, )

    def get(self, request, uid=0, format=None):
        size = self.request.query_params.get('size', 64)
        serializer = UserAvatarSerializer(data={
            'uid': uid,
            'size': size
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class UserImage(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JPGRenderer, )

    def get(self, request, img_id='', format=None):
        serializer = UserImageSerializer(data={
            'img_id': img_id
        }, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class UserAvatarManage(CreateAPIView):

    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserAvatarUploadSerializer
        return UserAvatarUpdateSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def patch(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.save()
        return Response(res)
