#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
    URLField,
    ValidationError,
)

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


class BoardCreateSerializer(Serializer):
    url = URLField()
    user = PrimaryKeyRelatedField(
        default=CurrentUserDefault(),
        read_only=True
    )

    def validate(self, data):
        netloc, path = normalize_url(data['url'])
        board_exists = Board.objects.filter(
            site__netloc=netloc,
            path=path
        ).exists()
        if board_exists:
            raise ValidationError('board already exists')
        data['netloc'] = netloc
        data['path'] = path
        return data

    def create(self, validated_data):
        user = validated_data['user']
        netloc = validated_data['netloc']
        path = validated_data['path']
        try:
            site = Site.objects.get(netloc=netloc)
        except Site.DoesNotExist:
            site = Site.objects.create(netloc=netloc, creator=user)
            site.save()
        board = Board.objects.create(
            site=site,
            path=path,
            title='{}{}'.format(netloc, path),
            creator=user
        )
        return board

    def to_representation(self, obj):
        return BoardSerializer(obj).data


class ThreadSerializer(ModelSerializer):
    board = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board')


class ThreadCreateSerializer(Serializer):
    title = CharField(max_length=100)
    board = PrimaryKeyRelatedField(queryset=Board.objects.all())
    text = CharField(max_length=65536)
    site = PrimaryKeyRelatedField(queryset=Site.objects.all())

    def create(self, validated_data):
        thread = Thread.objects.create(
            board=validated_data['board'],
            title=validated_data['title']
        )
        Post.objects.create(
            thread=thread,
            text=validated_data['text'],
            origin=validated_data['site']
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
