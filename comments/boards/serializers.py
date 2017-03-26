#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from authentication.serializers import UserSerializer

from .models import Board, Post, Site, Thread, Vote
from .url_processor import normalize_url


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ('id', 'netloc',)


class BoardSerializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'site', 'path', 'title')


class BoardDetailSerializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'site', 'path', 'title')
        read_only_fields = ('id', 'site', 'path')


class BoardByUrlSerializer(serializers.Serializer):
    url = serializers.URLField()

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


class ThreadSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board', 'creator', 'created')


class ThreadCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    url = serializers.URLField()
    text = serializers.CharField(max_length=65536)
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
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
            site=board.site,
            creator=user
        )
        return thread

    def to_representation(self, obj):
        return ThreadSerializer(obj).data


class ThreadDetailSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)
    post = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board', 'creator', 'created', 'post')
        read_only_fields = ('created',)

    def get_post(self, obj):
        post = obj.posts.filter(origin=None)[0]
        return PostSerializer(post).data


class PostSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    origin = serializers.PrimaryKeyRelatedField(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)
    number_of_children = serializers.IntegerField(read_only=True)
    own_vote = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'thread', 'parent', 'origin',
            'site', 'creator', 'created', 'number_of_children'
        )

    def get_own_vote(self, obj):
        try:
            vote = Vote.objects.get(post=obj, creator=self.context['request'].user)
            return 1 if vote.positive else -1
        except Vote.DoesNotExist:
            return 0


class PostCreateSerializer(serializers.ModelSerializer):
    origin = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())
    creator = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Post
        fields = (
            'text', 'origin',
            'site', 'creator',
        )

    def get_parent(self, origin):
        if not origin.parent or origin.parent == origin.origin:
            return origin
        return origin.parent

    def create(self, validated_data):
        post = Post.objects.create(
            thread=validated_data['origin'].thread,
            text=validated_data['text'],
            origin=validated_data['origin'],
            parent=self.get_parent(validated_data['origin']),
            site=validated_data['site'],
            creator=validated_data['creator']
        )
        return post

    def to_representation(self, obj):
        return PostSerializer(obj).data


class PostDetailSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    origin = serializers.PrimaryKeyRelatedField(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'thread', 'parent', 'origin',
            'site', 'creator', 'created'
        )
        read_only_fields = (
            'id', 'thread', 'parent', 'origin',
            'site', 'creator', 'created'
        )


class PostVotesSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    def validate(self, data):
        if data['value'] not in [-1, 1]:
            raise serializers.ValidationError('not allowed value!')
        return data

    def create(self, validated_data):
        return Vote.objects.create(
            post=validated_data['post'],
            positive=validated_data['value'] > 0,
            creator=validated_data['user']
        )

    def update(self, instance, validated_data):
        instance.positive = validated_data['value'] > 0
        instance.save()
        return instance

    def to_representation(self, obj):
        return {
            'value': 1 if obj.positive else -1
        }
