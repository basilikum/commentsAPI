#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from .models import Vote, VoteEntity


class VoteEntitySerializer(serializers.ModelSerializer):
    own = serializers.IntegerField()

    class Meta:
        model = VoteEntity
        fields = (
            'id', 'plus', 'minus', 'total', 'own'
        )

    def validate(self, data):
        if data['own'] not in [-1, 0, 1]:
            raise serializers.ValidationError('not allowed value!')
        return data

    def update(self, instance, validated_data):
        creator = self.context['request'].user
        value = self.validated_data['own']
        try:
            vote = Vote.objects.get(
                vote_entity=instance,
                creator=creator
            )
            if value == 0:
                vote.delete()
            else:
                vote.value = value
                vote.save()
        except Vote.DoesNotExist:
            if value != 0:
                Vote.objects.create(
                    vote_entity=instance,
                    value=value,
                    creator=creator
                )

        vote_entity = VoteEntity.objects \
            .prefetch_related('votes') \
            .get(id=instance.id)
        vote_entity.update()
        return vote_entity

    def to_representation(self, obj):
        votes = list(obj.votes.all())
        owns = [v for v in votes if v.creator_id == self.context['request'].user.id]
        if len(owns) > 0:
            own = owns[0].value
        else:
            own = 0
        return {
            'id': obj.id,
            'own': own,
            'plus': obj.plus,
            'minus': obj.minus,
            'total': obj.total
        }
