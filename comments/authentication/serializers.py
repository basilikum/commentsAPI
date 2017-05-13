#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserCreateSocialSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32, min_length=3)
    ext_picture_url = serializers.URLField(max_length=2000, allow_blank=True)
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
        user.ext_picture_url = validated_data['ext_picture_url']
        user.is_active = False
        user.save()
        return user
