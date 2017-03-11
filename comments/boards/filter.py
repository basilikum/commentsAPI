#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django_filters.rest_framework import FilterSet

from rest_framework.filters import BaseFilterBackend

from .models import Post
from .url_processor import normalize_url


class BoardsFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        board_ids = request.query_params.getlist('b', [])
        if len(board_ids) > 0:
            queryset = queryset.filter(board_id__in=board_ids)
        return queryset


class UrlFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        url = request.query_params.get('url', None)
        if url is not None:
            netloc, path = normalize_url(url)
            queryset = queryset.filter(
                site__netloc=netloc,
                path=path
            )
        return queryset


class PostFilter(FilterSet):

    class Meta:
        model = Post
        fields = ['thread']
