# -*- coding: utf-8 -*-

import json
import re
from functools import partial
from urlparse import urlparse

import scrapy


class GeneralSpider(scrapy.Spider):
    name = "general"
    url = None
    site = {}
    sites = {}
    limit = 1000
    counter = 0
    out_file = '/tmp/out.json'

    def start_requests(self):
        self.url = getattr(self, 'url', None)
        if not self.url:
            yield None
        self.site = {
            'linked_from': [],
            'linked_to': [],
            'sub_urls': {}
        }
        self.sites[''] = self.site
        self.update()
        yield scrapy.Request(url=self.url, callback=partial(self.parse, from_path=''))

    def parse(self, response, from_path=''):
        from_site = self.get_site(from_path)
        for link in response.css('a[href^="{}"], a[href^="/"]'.format(self.url)):
            next_page = link.css('::attr(href)').extract_first()
            next_page = response.urljoin(next_page)
            to_path = self.get_url_path(next_page)
            to_site = self.get_site(to_path)
            if to_site:
                existed = True
            else:
                to_site = self.create_site(to_path)
                existed = False
            to_site['linked_from'].append(from_path)
            from_site['linked_to'].append(to_path)
            self.update()
            if existed:
                continue
            self.counter += 1
            if self.counter > self.limit:
                break
            yield scrapy.Request(next_page, callback=partial(self.parse, from_path=to_path))


    def update(self):
        with open(self.out_file, 'w+') as f:
            json.dump(self.site, f, indent=4)

    def get_or_create_site(self, path):
        site = self.get_site(path)
        if site:
            return site
        return self.create_site(path)

    def get_site(self, path):
        return self.sites.get(path, None)

    def create_site(self, path):
        parts = self.get_path_parts(path)
        site = self.site
        for part in parts:
            if part not in site['sub_urls']:
                site['sub_urls'][part] = {
                    'linked_from': [],
                    'linked_to': [],
                    'sub_urls': {}
                }
            site = site['sub_urls'][part]
        self.sites[path] = site
        return site

    def get_path_parts(self, path):
        return path.split('/')

    def get_url_path(self, url):
        return re.sub('^/|/$', '', urlparse(url).path)
