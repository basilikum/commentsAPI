#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class EmailNullField(models.EmailField):
    description = "EmailField that stores NULL but returns ''."

    def from_db_value(self, value, expression, connection, contex):
        if value is None:
            return ''
        return value

    def to_python(self, value):
        if isinstance(value, models.EmailField):
            return value
        if value is None:
            return ''
        return value

    def get_prep_value(self, value):
        if value is '':
            return None
        return value
