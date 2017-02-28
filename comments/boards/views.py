#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filter import UrlFilterBackend
from .models import Board
from .serializers import BoardSerializer


class BoardListCreate(ListCreateAPIView):
    queryset = Board.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = BoardSerializer
    filter_backends = (UrlFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('site__netloc', 'path', 'title')
    ordering_fields = ('title', 'created')
    ordering = ('created',)

