#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Site, Board, Thread, Post, Vote


admin.site.register(Site, GuardedModelAdmin)
admin.site.register(Board, GuardedModelAdmin)
admin.site.register(Thread, GuardedModelAdmin)
admin.site.register(Post, GuardedModelAdmin)
admin.site.register(Vote, GuardedModelAdmin)
