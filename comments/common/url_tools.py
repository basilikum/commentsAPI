#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urlparse import parse_qs, urlparse


def parse_url(url, params=[]):
    parse_result = urlparse(url)
    parse_query_params = parse_qs(parse_result.query)
    query_string_parts = []
    params = params[:]
    params.sort()
    for param in params:
        if param not in parse_query_params:
            continue
        query_string_parts.append('{}={}'.format(param, parse_query_params[param]))
    return {
        'netloc': parse_result.netloc,
        'path': parse_result.path,
        'query_string': '?' + '&'.join(query_string_parts)
    }
