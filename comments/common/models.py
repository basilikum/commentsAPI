#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
from random import choice


def random_id(model, size, field_name='id'):
    chars = string.ascii_letters + string.digits + '_-'
    while True:
        mid = ''.join(choice(chars) for _ in range(size))
        kwargs = {field_name: mid}
        if not model.objects.filter(**kwargs).exists():
            break
    return mid

