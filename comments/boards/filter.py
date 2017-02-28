#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.filters import BaseFilterBackend

from common.url_tools import parse_url


class UrlFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        url = request.query_params.get('url', None)
        if url is not None:
            parsed_url = parse_url(url)
            queryset = queryset.filter(
                site__netloc=parsed_url['netloc'],
                path=parsed_url['path'] + parsed_url['query_string']
            )
        return queryset
