#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

from rest_framework.serializers import (
    CharField,
    ModelSerializer,
)

class UserSerializer(ModelSerializer):
    name = CharField(source='display_name')
    class Meta:
        model = get_user_model()
        fields = ('id', 'name',)
