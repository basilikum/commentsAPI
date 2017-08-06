#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from common.parsers import MultiPartJSONParser
from common.permissions import HasValidRecaptchaResponse
from common.renderer import JPGRenderer

from .serializers import (
    UserSerializer,
    UserCreateLocalSerializer,
    UserDetailSerializer,
    UserFinalizeLocalSerializer,
    UserImageSerializer,
    UserAvatarSerializer,
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


class UserMe(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = get_user_model().objects.all()
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class UserAvatar(APIView):
    permission_classes = ()
    renderer_classes = (JPGRenderer, )

    def get(self, request, uid=0, format=None):
        size = self.request.query_params.get('size', 64)
        if size == 'orig':
            size = 0
        serializer = UserAvatarSerializer(data={
            'uid': uid,
            'size': size
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class UserAvatarUpload(APIView):
    parser_classes = (MultiPartJSONParser, FormParser)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserAvatarUploadSerializer

    def post(self, request, format=None): # pylint: disable=W0613,W0622
        print dir(request)
        print request.data
        print request.POST
        print request.FILES
        if 'parent' not in request.data:
            request.data['parent'] = None
        serializer = UserAvatarUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        res = serializer.save()
        return Response(res, status=HTTP_201_CREATED)
