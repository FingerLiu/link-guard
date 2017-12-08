#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from ..items import BrokenItem
from app import redis_store


broken_links = set()


class LinkSpider(CrawlSpider):
    """
    TODO find a way to keep referer and title of broken href
    """

    name = 'link_spider'
    allow_domains = []
    start_urls = []
    handle_httpstatus_list = [404, 500, 403, 401, 400]
    broken_links = set()

    rules = (
        Rule(LxmlLinkExtractor(allow=(), allow_domains=['qrpay.ai']), callback='parse_obj', follow=True),
        Rule(LxmlLinkExtractor(allow=()), callback='parse_obj', follow=False),
    )

    def parse_obj(self, response):

        if response.status not in ('200', '302', '301', 200, 302, 301):
            print(self.start_domain)
            item = BrokenItem()
            item['url'] = response.url
            item['referer'] = response.request.headers.get('Referer', '').decode('utf-8')
            item['status'] = response.status

            # TODO put into pipline
            if item not in broken_links:
                link = json.dumps(dict(item))
                broken_links.add(link)
                redis_store.lpush('broken_links_%s' % (self.start_domain), link)
            return item
