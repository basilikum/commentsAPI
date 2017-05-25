#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import renderers


class JPGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpg'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data
