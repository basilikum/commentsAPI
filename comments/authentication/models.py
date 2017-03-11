#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from common.fields import EmailNullField


class CMUserManager(BaseUserManager):

    def _create_user(self, username, display_name, password, is_admin):
        user = self.model(
            username=username,
            display_name=display_name,
            is_admin=is_admin
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, display_name, password=None):
        return self._create_user(username, display_name, password, False)

    def create_superuser(self, username, display_name, password):
        return self._create_user(username, display_name, password, True)


class CMUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=120, blank=True)
    email = EmailNullField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    twitter = models.CharField(max_length=120, blank=True)
    google = models.CharField(max_length=120, blank=True)
    facebook = models.CharField(max_length=120, blank=True)

    objects = CMUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['display_name']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __unicode__(self):
        return u'{}'.format(self.username)
