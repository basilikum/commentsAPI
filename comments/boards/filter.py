#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django_filters.rest_framework import FilterSet

from rest_framework.filters import BaseFilterBackend

from .models import Post


class BoardsFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        board_ids = request.query_params.getlist('b', [])
        if len(board_ids) > 0:
            queryset = queryset.filter(board_id__in=board_ids)
        return queryset


class PostFilter(FilterSet):

    class Meta:
        model = Post
        fields = ['thread', 'parent']
