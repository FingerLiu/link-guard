#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess

from app import celery, redis_store
from .spiders.link_spider import LinkSpider



broken_links = set()


class LinkGuard(object):
    """docstring for LinkGuard"""
    def __init__(self, domain, base_url):
        self.domain = domain
        self.base_url = base_url

    def guard(self):
        """check all links in the given url"""
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })
        kwargs = {
            'start_domain': self.domain,
            'start_urls': [self.base_url],
            'allow_domains': [],
            'rules': (
                Rule(LxmlLinkExtractor(allow=(), allow_domains=[self.domain]), callback='parse_obj', follow=True),
                Rule(LxmlLinkExtractor(allow=()), callback='parse_obj', follow=False),
            )
        }

        # clear old record
        redis_store.delete('broken_links_%s' % (self.domain))

        process.crawl(LinkSpider, **kwargs)
        process.start()
        return True


@celery.task()
def guard(domain='dev.qrpay.ai', base_url='https://dev.qrpay.ai'):
    """docstring for main"""
    lg = LinkGuard(domain, base_url)
    lg.guard()
    print('brokens are ')
    print(redis_store.lrange('broken_links_%s' % (domain), 0, -1))


@celery.task()
def daily_guard():
    """check for all registered domain every day"""
    # TODO change to get tasks from dbtable Link
    guard_tasks = redis_store.lrange('link_gurad_daily_tasks', 0, -1)
    for task_str in guard_tasks:
        task = json.loads(task_str)
        lg = LinkGuard(task['domain'], task['base_url'])
        lg.guard()
        print('brokens are ')
        print(redis_store.lrange('broken_links_%s' % (task['domain']), 0, -1))


if __name__ == '__main__':
    guard()
