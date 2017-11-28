# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['dev.qrpay.ai']
    start_urls = ['https://dev.qrpay.ai/']

    def parse(self, response):
        print(111)
