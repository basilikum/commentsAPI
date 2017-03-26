#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models import Count

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter import (
    BoardsFilterBackend,
    PostFilter,
)
from .models import Board, Post, Thread, Vote
from .pagination import StandardPagination
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardByUrlSerializer,
    PostSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostVotesSerializer,
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
    queryset = Post.objects \
        .prefetch_related('votes') \
        .annotate(number_of_children=Count('children')) \
        .order_by('created') \
        .all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = PostFilter
    search_fields = ('text',)
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer


class PostChildren(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('text',)

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Post.objects \
            .annotate(Count('votes')) \
            .order_by('created') \
            .filter(parent_id=pk) \
            .exclude(parent__parent=None)


class PostVotes(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def patch(self, request, **kwargs):
        try:
            post = Post.objects.get(pk=kwargs['pk'])
        except Post.DoesNotExist:
            raise
        value = request.data['value']
        if value == 0:
            Vote.objects.filter(post=post, creator=request.user).delete()
            return Response({'value': 0})
        data = {
            post: post,
            value: value
        }
        try:
            vote = Vote.objects.get(post=post, creator=request.user)
            serializer = PostVotesSerializer(vote, data)
        except Vote.DoesNotExist:
            serializer = PostVotesSerializer(data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class PostDetail(RetrieveUpdateAPIView):
    queryset = Post.objects.prefetch_related('votes').all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PostDetailSerializer
