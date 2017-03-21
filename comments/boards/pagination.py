#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'page_size': self.page_size,
            'count': self.page.paginator.count,
            'results': data
        })
