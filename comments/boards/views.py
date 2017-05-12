#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models import Count, Sum
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAdminUser

from common.permissions import IsActiveOrReadOnly

from .filter import (
    BoardsFilterBackend,
    PostFilter,
)
from .models import Board, Post, Site, Thread
from .pagination import StandardPagination
from .permissions import IsOwnerAndPostIsNotOlderThan
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardByUrlSerializer,
    PostSerializer,
    PostComplexSerializer,
    PostCreateSerializer,
    SiteSerializer,
    SiteDetailSerializer,
    ThreadSerializer,
    ThreadCreateSerializer,
    ThreadDetailSerializer
)


def annotated_posts():
    return Post.objects.annotate(votes_sum=Sum('votes__value'))


class SiteListCreate(ListCreateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('netloc',)
    ordering_fields = ('netloc', 'created')
    ordering = ('netloc',)


class SiteDetail(RetrieveUpdateAPIView):
    queryset = Site.objects.prefetch_related('re_rules', 'qs_rules').all()
    serializer_class = SiteDetailSerializer
    permission_classes = (IsAdminUser,)


class BoardList(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (IsActiveOrReadOnly,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('site__netloc', 'path', 'title')
    ordering_fields = ('title', 'created')
    ordering = ('created',)
    pagination_class = StandardPagination


class BoardDetail(RetrieveUpdateAPIView):
    queryset = Board.objects.all()
    permission_classes = (IsActiveOrReadOnly,)
    serializer_class = BoardDetailSerializer


class BoardByUrl(RetrieveAPIView):
    permission_classes = (IsActiveOrReadOnly,)
    serializer_class = BoardByUrlSerializer

    def get_object(self):
        return {
            'url': self.request.query_params.get('url', '')
        }


class ThreadListCreate(ListCreateAPIView):
    queryset = Thread.objects \
        .annotate(
            number_of_children=Count('original_post__children', distinct=True),
            number_of_descendants=Count('original_post__children__children', distinct=True)
        ) \
        .select_related('original_post', 'original_post__vote_entity') \
        .prefetch_related('original_post__vote_entity__votes') \
        .all()
    permission_classes = (IsActiveOrReadOnly,)
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
    queryset = Thread.objects.select_related('creator').all()
    permission_classes = (IsActiveOrReadOnly,)
    serializer_class = ThreadDetailSerializer

    def get_serializer_context(self):
        return {
            'request': self.request
        }


class PostListCreate(ListCreateAPIView):
    permission_classes = (IsActiveOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = PostFilter
    search_fields = ('text',)
    ordering_fields = (
        'modified',
        'created',
        'vote_entity__total',
        'vote_entity__plus',
        'number_of_children'
    )
    ordering = ('-modified',)
    pagination_class = StandardPagination

    def get_queryset(self):
        posts = Post.objects \
            .annotate(
                number_of_children=Count('children', distinct=True),
            ) \
            .prefetch_related('vote_entity__votes') \
            .select_related('creator', 'vote_entity')
        if 'complex' in self.request.query_params:
            posts = posts.select_related(
                'thread', 'thread__board', 'site'
            )
        return posts


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        if 'complex' in self.request.query_params:
            return PostComplexSerializer
        return PostSerializer


class PostChildren(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (IsActiveOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('text',)

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Post.objects \
            .prefetch_related('vote_entity__votes') \
            .select_related('creator', 'vote_entity') \
            .filter(parent_id=pk) \
            .exclude(parent__parent=None) \
            .order_by('created')


class PostDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsActiveOrReadOnly, IsOwnerAndPostIsNotOlderThan)
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects \
            .annotate(
                number_of_children=Count('children', distinct=True),
            ) \
            .prefetch_related('vote_entity__votes') \
            .select_related('creator', 'vote_entity')
