#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError


def validate_vote_value(value):
    if value not in [-1, 1]:
        raise ValidationError('{} is neither 1 nor -1'.format(value))
