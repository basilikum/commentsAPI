#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Vote, VoteEntity


admin.site.register(Vote, GuardedModelAdmin)
admin.site.register(VoteEntity, GuardedModelAdmin)
