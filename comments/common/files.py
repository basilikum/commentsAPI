#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path


def ensure(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name
