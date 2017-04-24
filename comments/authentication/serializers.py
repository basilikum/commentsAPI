#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

from rest_framework import serializers

from .jwt_helper import (
    jwt_encode,
    get_payload,
)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username')
    class Meta:
        model = get_user_model()
        fields = ('id', 'name',)


class UserCreateSocialSerializer(serializers.BaseSerializer):
    username = serializers.CharField(max_length=32, min_length=3)
    soc_id = serializers.CharField(max_length=120)
    soc_provider = serializers.ChoiceField(
        choices=['google', 'twitter', 'facebook']
    )

    def validate(self, data):
        User = get_user_model()
        username = data['username']
        num = 1
        basename = username
        while User.objects.filter(username=username).exists():
            appendix = str(num)
            overflow = max(0, len(basename) + len(appendix) - 32)
            if overflow > 0:
                basename = basename[:-overflow]
            username = '{}{}'.format(basename, num)
        data['username'] = username
        return data

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(validated_data['username'], '')
        setattr(user, validated_data['soc_provider'], validated_data['soc_id'])
        user.is_active = False
        user.save()
        return user


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
