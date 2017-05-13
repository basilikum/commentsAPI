#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from users.serializers import UserSerializer
from votes.models import VoteEntity
from votes.serializers import VoteEntitySerializer

from .models import Board, Post, Site, Thread, QsRule, ReRule
from .url_processor import normalize_url


class QsRuleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = QsRule
        fields = ('id', 'path', 'params')


class ReRuleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = ReRule
        fields = ('id', 'regex', 'repl')


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ('id', 'netloc',)


class SiteDetailSerializer(serializers.ModelSerializer):
    qs_rules = QsRuleSerializer(many=True)
    re_rules = ReRuleSerializer(many=True)
    class Meta:
        model = Site
        fields = ('id', 'netloc', 'qs_rules', 're_rules')



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


class OriginalPostSerializer(serializers.ModelSerializer):
    vote_entity = VoteEntitySerializer()

    class Meta:
        model = Post
        fields = (
            'id', 'creator', 'created', 'vote_entity'
        )


class ThreadSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)
    original_post = OriginalPostSerializer(read_only=True)
    number_of_children = serializers.IntegerField(read_only=True)
    number_of_descendants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Thread
        fields = (
            'id', 'title', 'board', 'raw_path',
            'creator', 'created', 'original_post',
            'number_of_children', 'number_of_descendants'
        )


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
        post = Post.objects.create(
            thread=thread,
            text=validated_data['text'],
            site=board.site,
            creator=user,
            vote_entity=VoteEntity.objects.create(
                creator=user
            )
        )
        thread.original_post = post
        thread.save()
        return thread

    def to_representation(self, obj):
        return ThreadSerializer(obj).data


class ThreadDetailSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board', 'creator', 'created')
        read_only_fields = ('created',)


class ThreadComplexSerializer(serializers.ModelSerializer):
    board = BoardSerializer(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board', 'creator', 'created', 'raw_path')
        read_only_fields = ('created',)


class PostSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    origin = serializers.PrimaryKeyRelatedField(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)
    number_of_children = serializers.IntegerField(read_only=True)
    vote_entity = VoteEntitySerializer()

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'thread', 'parent', 'origin',
            'site', 'creator', 'created', 'number_of_children',
            'vote_entity', 'modified'
        )


class PostComplexSerializer(PostSerializer):
    thread = ThreadComplexSerializer(read_only=True)
    site = SiteSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'thread', 'parent', 'origin',
            'site', 'creator', 'created', 'number_of_children',
            'vote_entity', 'modified'
        )


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
        if not origin.parent or not origin.parent.parent:
            return origin
        return origin.parent

    def create(self, validated_data):
        parent = self.get_parent(validated_data['origin'])
        post = Post.objects.create(
            thread=validated_data['origin'].thread,
            text=validated_data['text'],
            origin=validated_data['origin'],
            parent=parent,
            site=validated_data['site'],
            creator=validated_data['creator'],
            vote_entity=VoteEntity.objects.create(
                creator=validated_data['creator']
            )
        )
        parent.save()
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
