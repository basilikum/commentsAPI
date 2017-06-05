#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import traceback

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser, DataAndFiles

from django.conf import settings
from django.http.multipartparser import MultiPartParser, MultiPartParserError
from django.utils import six


class MultiPartJSONParser(BaseParser):
    media_type = 'multipart/form-data'

    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        request = parser_context['request']
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        meta = request.META.copy()
        meta['CONTENT_TYPE'] = media_type
        upload_handlers = request.upload_handlers
        try:
            parser = MultiPartParser(meta, stream, upload_handlers, encoding)
            data, files = parser.parse()
            data = data.copy()
            for key in data:
                if data[key]:
                    try:
                        value = json.loads(data[key])
                        if isinstance(value, list):
                            data.setlist(key, value)
                        else:
                            data[key] = value
                    except ValueError:
                        pass
            return DataAndFiles(data, files)
        except MultiPartParserError as exc:
            print traceback.format_exc()
            raise ParseError('Multipart form parse error - %s' % six.text_type(exc))
