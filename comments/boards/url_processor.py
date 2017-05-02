#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from urlparse import parse_qs, urlparse

from .models import Site, QsRule


def normalize_url(url):
    netloc, path, query_params = get_url_parts(url)
    try:
        site = Site.objects \
            .prefetch_related('re_rules') \
            .get(netloc=netloc)
    except Site.DoesNotExist:
        return netloc, path
    path = apply_re_rules(path, site.re_rules.all())
    try:
        qs_rule = QsRule.objects.get(sites=site, path=path)
    except QsRule.DoesNotExist:
        return netloc, path
    qstring = qs_rule.apply(query_params)
    return netloc, path + qstring


def normalize_path(path):
    path = re.sub('^/|/$', '', path.strip())
    if len(path) > 0:
        return '/' + path
    return ''


def apply_re_rules(path, re_rules):
    for re_rule in re_rules:
        path = re_rule.apply(path)
    return path


def get_url_parts(url):
    parse_result = urlparse(url)
    path = normalize_path(parse_result.path)
    netloc = parse_result.netloc
    query_params = parse_qs(parse_result.query)
    return netloc, path, query_params
