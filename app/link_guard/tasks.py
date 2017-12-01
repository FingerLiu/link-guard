#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from app import celery, redis_store
from ..models import Link
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


def dump_links2db():
    """docstring for dump_links2db"""
    # TODO here
    pass


@periodic_task(run_every=(crontab(minute='1', hour='4')))
def daily_guard():
    """check for all registered domain every day"""
    # TODO change to get tasks from dbtable Link
    tasks = Link.query.all()
    for link in tasks:
        lg = LinkGuard(link.domain, task.base_url)
        lg.guard()
        print('brokens are ')
        print(redis_store.lrange('broken_links_%s' % (task['domain']), 0, -1))
    dump_links2db()


if __name__ == '__main__':
    guard()
