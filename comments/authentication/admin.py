#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import CMUser


admin.site.register(CMUser, GuardedModelAdmin)
