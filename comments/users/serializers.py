#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from cStringIO import StringIO

import magic

from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

from authentication.jwt_helper import (
    jwt_encode,
    get_payload,
)

from common.files import ensure
from common.models import random_id


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
    size = serializers.IntegerField(min_value=0)
    uid = serializers.SlugField()

    def validate(self, data):
        User = get_user_model()
        if not User.objects.filter(uid=data['uid']).exists:
            raise serializers.ValidationError('User does not exist!')
        file_path = os.path.join(
            settings.USER_PROFILE_PATH,
            data['uid'],
            '{}.jpg'.format(data['size']) if data['size'] > 0 else 'original.jpg'
        )
        if not os.path.exists(file_path):
            raise serializers.ValidationError('File does not exist!')
        return open(file_path, 'r')


class UserImageSerializer(serializers.Serializer):
    img_id = serializers.SlugField()
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    def validate(self, data):
        file_path = os.path.join(
            settings.USER_PROFILE_PATH,
            data['user'].uid,
            '{}.jpg'.format(data['img_id'])
        )
        print file_path
        if not os.path.exists(file_path):
            raise serializers.ValidationError('File does not exist!')
        return open(file_path, 'r')


class UserAvatarUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    x = serializers.IntegerField(min_value=0)
    y = serializers.IntegerField(min_value=0)
    size = serializers.IntegerField(min_value=1)
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
        file_imgdata = StringIO(ufile.read())
        ufile.seek(0)
        img = Image.open(file_imgdata)
        if data['x'] >= img.size[0] or data['y'] >= img.size[1]:
            raise serializers.ValidationError('Crop values exceed image size!')
        data['size'] = min(data['size'], img.size[0] - data['x'], img.size[1] - data['y'])
        return data

    def save(self):
        ufile = self.validated_data['file']
        user_profile_path = os.path.join(
            settings.USER_PROFILE_PATH,
            self.validated_data['user'].uid
        )
        tmp_path = ensure(os.path.join(user_profile_path, 'tmp'))
        file_path = os.path.join(tmp_path, str(ufile))
        res_path = os.path.join(user_profile_path, 'original.jpg')
        with open(file_path, 'wb+') as destination:
            for chunk in ufile.chunks():
                destination.write(chunk)
        img = Image.open(file_path)
        img.save(res_path)
        os.remove(file_path)
        self.crop(
            res_path,
            self.validated_data['x'],
            self.validated_data['y'],
            self.validated_data['size']
        )
        return {
            'success': True
        }

    def crop(self, file_path, x0, y0, size):
        x1 = x0 + size
        y1 = y0 + size
        img = Image.open(file_path)
        img = img.crop((x0, y0, x1, y1))
        for size in [64, 128, 256]:
            target_path = os.path.join(
                settings.USER_PROFILE_PATH,
                self.validated_data['user'].uid,
                '{}.jpg'.format(size)
            )
            img.resize((size, size)).save(target_path)
