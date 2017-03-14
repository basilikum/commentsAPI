#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filter import (
    BoardsFilterBackend,
    PostFilter,
)
from .models import Board, Post, Thread
from .pagination import StandardPagination
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardByUrlSerializer,
    PostSerializer,
    PostDetailSerializer,
    ThreadSerializer,
    ThreadCreateSerializer,
    ThreadDetailSerializer
)


class BoardList(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('site__netloc', 'path', 'title')
    ordering_fields = ('title', 'created')
    ordering = ('created',)
    pagination_class = StandardPagination


class BoardDetail(RetrieveUpdateAPIView):
    queryset = Board.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = BoardDetailSerializer


class BoardByUrl(RetrieveAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = BoardByUrlSerializer

    def get_object(self):
        return {
            'url': self.request.query_params.get('url', '')
        }


class ThreadListCreate(ListCreateAPIView):
    queryset = Thread.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (BoardsFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('title',)
    ordering_fields = ('title', 'created')
    ordering = ('created',)
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ThreadCreateSerializer
        return ThreadSerializer


class ThreadDetail(RetrieveUpdateAPIView):
    queryset = Thread.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ThreadDetailSerializer


class PostListCreate(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = PostFilter
    search_fields = ('text',)
    ordering_fields = ('created',)
    ordering = ('created',)
    pagination_class = StandardPagination


class PostDetail(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PostDetailSerializer
