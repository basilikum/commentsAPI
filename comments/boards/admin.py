#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Site, Board, Thread, Post, QsRule, ReRule


admin.site.register(Site, GuardedModelAdmin)
admin.site.register(Board, GuardedModelAdmin)
admin.site.register(Thread, GuardedModelAdmin)
admin.site.register(Post, GuardedModelAdmin)

admin.site.register(QsRule, GuardedModelAdmin)
admin.site.register(ReRule, GuardedModelAdmin)
