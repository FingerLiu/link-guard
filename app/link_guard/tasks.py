#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse
from bson import json_util
from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from app import celery, redis_store, db
from app.models import Link, Result
from app.link_guard import settings as custom_settings
from app.link_guard.spiders.link_spider import LinkSpider


broken_links = set()


def get_domain(url):
    """docstring for get_domain"""
    parsed_url = urlparse(url)
    return parsed_url.netloc


class LinkGuard(object):
    """docstring for LinkGuard"""
    def __init__(self, domain, base_url):
        self.base_url = base_url
        self.domain = get_domain(base_ur)

    def dump_links2db(self, res):
        res_dumped = json.dumps(res, default=json_util.default)
        result = Result(domain=self.domain, result=res_dumped)
        db.session.add(result)
        db.session.commit()

        raw_broken_links = redis_store.lrange('broken_links_%s' % (self.domain), 0, -1)
        broken_links = [link.decode() for link in raw_broken_links]
        link = Link.query.filter_by(domain=self.domain).first()
        link.broken_links = broken_links
        link.last_check_result_id = result.id
        if broken_links:
            link.status = 'Failed'
        else:
            link.status = 'OK'
        db.session.add(link)
        db.session.commit()

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
        res = spider.stats.get_stats()
        self.dump_links2db(res)
        return res


@celery.task()
def guard(domain='dev.qrpay.ai', start_url='https://dev.qrpay.ai'):
    """docstring for main"""
    lg = LinkGuard(domain, start_url)
    lg.guard()
    print('brokens are ')
    print(redis_store.lrange('broken_links_%s' % (domain), 0, -1))
    return True


@periodic_task(run_every=(crontab(minute='1', hour='4')))
def daily_guard():
    """check for all registered domain every day"""
    # TODO for effiective write a batch guard rather than use the single guard
    links = Link.query.all()
    for link in links:
        lg = LinkGuard(link.domain, link.base_url)
        lg.guard()
        print('brokens are ')
        print(redis_store.lrange('broken_links_%s' % (link['domain']), 0, -1))
    return True


if __name__ == '__main__':
    guard()
