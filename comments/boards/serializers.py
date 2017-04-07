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


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = (
            'value',
        )


class PostSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    origin = serializers.PrimaryKeyRelatedField(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)
    number_of_children = serializers.IntegerField(read_only=True)
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'thread', 'parent', 'origin',
            'site', 'creator', 'created', 'number_of_children',
            'votes', 'modified'
        )

    def get_votes(self, obj):
        return PostVotesSerializer(obj, context=self.context).data


class ThreadDetailSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'board', 'creator', 'created')
        read_only_fields = ('created',)


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
        parent = self.get_parent(validated_data['origin'])
        post = Post.objects.create(
            thread=validated_data['origin'].thread,
            text=validated_data['text'],
            origin=validated_data['origin'],
            parent=parent,
            site=validated_data['site'],
            creator=validated_data['creator']
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


class PostVotesSerializer(serializers.ModelSerializer):
    own = serializers.IntegerField(source='votes_own')
    plus = serializers.IntegerField(source='votes_plus', read_only=True)
    minus = serializers.IntegerField(source='votes_minus', read_only=True)

    class Meta:
        model = Post
        fields = (
            'plus', 'minus', 'own'
        )

    def validate(self, data):
        print data
        if data['votes_own'] not in [-1, 0, 1]:
            raise serializers.ValidationError('not allowed value!')
        return data

    def update(self, instance, validated_data):
        creator = self.context['request'].user
        value = self.validated_data['votes_own']
        try:
            vote = Vote.objects.get(post=instance, creator=creator)
            if value == 0:
                vote.delete()
            else:
                vote.value = value
                vote.save()
        except Vote.DoesNotExist:
            if value != 0:
                Vote.objects.create(
                    post=instance,
                    value=value,
                    creator=creator
                )

        return Post.objects.prefetch_related('votes').get(id=instance.id)

    def to_representation(self, obj):
        votes = list(obj.votes.all())
        plus = len([v for v in votes if v.value == 1])
        minus = len([v for v in votes if v.value == -1])
        owns = [v for v in votes if v.creator_id == self.context['request'].user.id]
        if len(owns) > 0:
            own = owns[0].value
        else:
            own = 0
        return {
            'own':own,
            'plus': plus,
            'minus': minus
        }
