#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from app import celery, redis_store
from app.models import Link
from app.link_guard import settings as custom_settings
from app.link_guard.spiders.link_spider import LinkSpider


broken_links = set()


class LinkGuard(object):
    """docstring for LinkGuard"""
    def __init__(self, domain, base_url):
        self.domain = domain
        self.base_url = base_url

    def guard(self):
        """check all links in the given url"""
        settings = get_project_settings()
        settings.setmodule(custom_settings)
        process = CrawlerProcess(settings)
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

        spider = Crawler(LinkSpider, settings)

        process.crawl(spider, **kwargs)
        process.start()
        print(spider.stats.get_stats())
        res = spider.stats.get_stats()
        return res


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
