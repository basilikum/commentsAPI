#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
from random import choice


def random_id(model, size):
    chars = string.ascii_letters + string.digits + '_-'
    while True:
        mid = ''.join(choice(chars) for _ in range(size))
        if not model.objects.filter(id=mid).exists():
            break
    return mid

