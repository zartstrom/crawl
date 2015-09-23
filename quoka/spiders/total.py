

import json
import re

import scrapy

from quoka.spiders.properties import POST_DATA


class TotalSpider(scrapy.Spider):
    name = "total"
    allowed_domains = ["quoka.de"]
    start_urls = [
        "http://www.quoka.de/immobilien/bueros-gewerbeflaechen/"
    ]

    def parse(self, response):
        POST_DATA["comm"] = "all"
        body = json.dumps(POST_DATA)

        url = self.start_urls[0]

        yield scrapy.Request(url, self.parse_total, method="POST", body=body, dont_filter=True)

    def parse_total(self, response):
        for total_str in response.css('ul #NAVI_CAT_27 > li > span::text').extract():
            total = int(re.sub(r"\D", "", total_str))
            print total
            yield {'total': total}
