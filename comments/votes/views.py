#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.generics import RetrieveUpdateAPIView

from common.permissions import IsActiveOrReadOnly

from .models import VoteEntity
from .permissions import IsNotOwner
from .serializers import VoteEntitySerializer


class Votes(RetrieveUpdateAPIView):
    permission_classes = (IsActiveOrReadOnly, IsNotOwner)
    serializer_class = VoteEntitySerializer

    def get_queryset(self):
        return VoteEntity.objects \
            .prefetch_related('votes')

    def get_serializer_context(self):
        return {
            'request': self.request
        }
