#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import magic

from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

from authentication.jwt_helper import (
    jwt_encode,
    get_payload,
)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username')
    has_avatar = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('uid', 'name', 'created', 'has_avatar')

    def get_has_avatar(self, obj):
        file_path = os.path.join(
            settings.USER_PROFILE_PATH,
            obj.uid,
            '{}.png'.format(64)
        )
        return os.path.exists(file_path)


class UserCreateLocalSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32, min_length=3)
    password = serializers.CharField(min_length=8)
    email = serializers.EmailField(max_length=255)

    def create(self, validated_data):
        User = get_user_model()
        return User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )

    def to_representation(self, obj):
        payload = get_payload(obj)
        token = jwt_encode(payload)
        return {
            'token': token
        }


class UserFinalizeLocalSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32, min_length=3)

    def update(self, user, validated_data):
        user.username = validated_data['username']
        user.is_active = True
        user.save()
        return user

    def to_representation(self, obj):
        payload = get_payload(obj)
        token = jwt_encode(payload)
        return {
            'token': token
        }


class UserAvatarSerializer(serializers.Serializer):
    size = serializers.IntegerField(min_value=1)
    uid = serializers.SlugField()

    def validate(self, data):
        User = get_user_model()
        if not User.objects.filter(uid=data['uid']).exists:
            raise serializers.ValidationError('User does not exist!')
        file_path = os.path.join(
            settings.USER_PROFILE_PATH,
            data['uid'],
            '{}.jpg'.format(data['size'])
        )
        if not os.path.exists(file_path):
            raise serializers.ValidationError('File does not exist!')
        return open(file_path, 'r')


class UserAvatarUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    def validate(self, data):
        MAX_FILE_SIZE = 52428800 # 50MB
        MIME_TYPES = [
            'image/jpeg',
            'image/png',
            'image/gif'
        ]
        ufile = data['file']
        size = ufile.size
        if size > MAX_FILE_SIZE:
            raise serializers.ValidationError('exeeded file size limit (50MB)')
        mimetype = magic.from_buffer(ufile.read(), mime=True)
        ufile.seek(0)
        if mimetype not in MIME_TYPES:
            raise serializers.ValidationError('not supported file type')
        return data

    def save(self):
        ufile = self.validated_data['file']
        file_path = os.path.join(
            settings.USER_PROFILE_PATH,
            self.validated_data['user'].uid,
            'tmp',
            str(ufile)
        )
        res_path = os.path.join(
            settings.USER_PROFILE_PATH,
            self.validated_data['user'].uid,
            'tmp',
            'raw.jpg'
        )
        with open(file_path, 'wb+') as destination:
            for chunk in ufile.chunks():
                destination.write(chunk)
        img = Image.open(file_path)
        img.save(res_path)
