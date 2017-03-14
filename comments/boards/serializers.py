#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
    URLField,
)

from authentication.serializers import UserSerializer

from .models import Board, Post, Site, Thread
from .url_processor import normalize_url


class SiteSerializer(ModelSerializer):
    class Meta:
        model = Site
        fields = ('id', 'netloc',)


class BoardSerializer(ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'site', 'path', 'title')


class BoardDetailSerializer(ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'site', 'path', 'title')
        read_only_fields = ('id', 'site', 'path')


class BoardByUrlSerializer(Serializer):
    url = URLField()

    def to_representation(self, data):
        netloc, path = normalize_url(data['url'])
        try:
            board = Board.objects.select_related('site') \
                .get(site__netloc=netloc, path=path)
            return BoardSerializer(board).data
        except Board.DoesNotExist:
            try:
                site = Site.objects.get(netloc=netloc)
                site = SiteSerializer(site).data
            except Site.DoesNotExist:
                site = {
                    'id': 'fake',
                    'netloc': netloc
                }
            return {
                'id': 'fake',
                'path': path,
                'title': '{}{}'.format(netloc, path),
                'site': site
            }


class ThreadSerializer(ModelSerializer):
    board = PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board', 'creator', 'created')


class ThreadCreateSerializer(Serializer):
    title = CharField(max_length=100)
    url = URLField()
    text = CharField(max_length=65536)
    site = PrimaryKeyRelatedField(queryset=Site.objects.all())
    user = PrimaryKeyRelatedField(
        default=CurrentUserDefault(),
        read_only=True
    )

    def create(self, validated_data):
        netloc, path = normalize_url(validated_data['url'])
        user = validated_data['user']
        try:
            board = Board.objects.select_related('site') \
                .get(site__netloc=netloc, path=path)
        except Board.DoesNotExist:
            try:
                site = Site.objects.get(netloc=netloc)
            except Site.DoesNotExist:
                site = Site.objects.create(netloc=netloc, creator=user)
            board = Board.objects.create(
                site=site,
                path=path,
                title='{}{}'.format(netloc, path),
                creator=user
            )
        thread = Thread.objects.create(
            board=board,
            title=validated_data['title'],
            raw_path=validated_data['url'],
            creator=user
        )
        Post.objects.create(
            thread=thread,
            text=validated_data['text'],
            origin=board.site,
            creator=user
        )
        return thread

    def to_representation(self, obj):
        return ThreadSerializer(obj).data


class ThreadDetailSerializer(ModelSerializer):
    board = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'board', 'title')
        read_only_fields = ('id', 'board')


class PostSerializer(ModelSerializer):
    parent = PrimaryKeyRelatedField(queryset=Post.objects.all())
    thread = PrimaryKeyRelatedField(read_only=True)
    origin = PrimaryKeyRelatedField(queryset=Site.objects.all())

    class Meta:
        model = Post
        fields = ('id', 'text', 'thread', 'parent', 'origin')
        read_only_fields = ('id', 'thread')

    def create(self, validated_data):
        post = Post.objects.create(
            thread=validated_data['parent'].thread,
            text=validated_data['text'],
            parent=validated_data['parent'],
            origin=validated_data['origin']
        )
        return post


class PostDetailSerializer(ModelSerializer):
    parent = PrimaryKeyRelatedField(read_only=True)
    thread = PrimaryKeyRelatedField(read_only=True)
    origin = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'text', 'thread', 'parent', 'origin')
        read_only_fields = ('id', 'thread', 'parent', 'origin')
