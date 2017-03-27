#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models import Count, Case, When, CharField, IntegerField

from .models import Post


def posts_with_votes():
    return Post.objects.annotate(
        plus1s=Count(Case(
            When(votes__positive=True, then=1),
            output_field=CharField(),
        )),
        minus1s=Count(Case(
            When(votes__positive=False, then=1),
            output_field=CharField(),
        ))
    )
