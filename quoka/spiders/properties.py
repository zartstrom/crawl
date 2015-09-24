# -*- coding: utf-8 -*-


from collections import defaultdict
from datetime import date
import json
import re

import scrapy

from quoka.items import PropertyItem, PropertyLoader


def add_scheme_host(string):
    return "http://www.quoka.de%s" % string


def get_nof_pages(response):
    """get the numbers of pages in pagination in the context of city"""
    selector = response.css("div .Column > ul > li > a > strong:nth-child(2)::text").extract()
    try:
        result = int(selector[0])
    except (IndexError, ValueError):
        result = 0

    return result


def get_url_format(response):
    """get url pattern for pages from 2 to n

    result example:
        http://www.quoka.de/kleinanzeigen/cat_27_2710_ct_111756_page_%d.html
    """
    selector = response.css("div .Column > ul > li:nth-child(5) > a::attr(\"href\")").extract()

    part = re.sub(r"_\d+.html", "_%d.html", selector[0])

    assert "%d" in part

    return add_scheme_host(part)


# probably not all parameters necessary
POST_DATA = {
    "catid": "27_2710",
    "cityid": "0",
    "classtype": "of",  # -> "nur Angebote"
    "comm": "all",
    "detailgeosearch": "true",
    "dispads": "20",
    "mask": "default",
    "mode": "search",
    "notepageno": "1",
    "pageno": "1",
    "pndu": "/kleinanzeigen/cat_27_2710_ct_0_page_2.html",
    "pnno": "1",
    "pntp": "277",
    "pnur": "/immobilien/bueros-gewerbeflaechen/",
    "pnuu": "/immobilien/bueros-gewerbeflaechen/",
    "pricelow": "von",
    "pricetop": "bis",
    "radius": "25",
    "result": "small",
    "searchbool": "and",
    "searchbutton": "true",
    "showallresults": "true",  # before was 'false'
    "showmorecatlink": "true",
    "sorting": "adsort",
    "suburbid": "0",
    "tlc": "2"
}


class PropertiesSpider(scrapy.Spider):
    name = "properties"
    allowed_domains = ["quoka.de"]
    start_urls = [
        "http://www.quoka.de/immobilien/bueros-gewerbeflaechen/"
    ]

    def __init__(self):
        #self.stats = defaultdict(int)  # stats
        super(PropertiesSpider, self).__init__()

    def parse(self, response):
        """set filters in post data

        post parameter classtype is in ["all", "of", "wa"],
        which correspond to "Keine Einschränkung", "nur Angebote" und "nur Gesuche"

        post parameter comm is in ["all", 0, 1],
        which correspond to "Keine Einschränkung", "nur Private", "nur Gewerbliche"
        """
        meta = {
            "property_type": "Büros, Gewerbeflächen"
        }

        for commercial in [0, 1]:
            POST_DATA["comm"] = commercial
            body = json.dumps(POST_DATA)
            meta["commercial"] = commercial

            url = self.start_urls[0]

            yield scrapy.Request(
                url, self.parse_cities, meta=meta, method="POST", body=body, dont_filter=True)

    def parse_cities(self, response):
        """crawl cities"""

        pattern_city_href = r".*gewerbeflaechen/\w+/cat_27_2710_ct_\d+.html"
        #pattern_city_href = r".*gewerbeflaechen/koeln/cat_27_2710_ct_\d+.html"

        for url in response.css("div .cnt ul li ul li a::attr(\"href\")").re(pattern_city_href):  # [:1]:
            pattern = r".*gewerbeflaechen/(\w+)/cat_27_2710_ct_\d+.html"
            city_category = re.match(pattern, url).group(1)  # for stats
            response.meta["city_category"] = city_category

            yield scrapy.Request(
                response.urljoin(url), self.parse_pages,
                meta=response.meta,
                dont_filter=True)

    def parse_pages(self, response):
        """crawl pages for a city

        url pattern from first page differs from url pattern of the following pages. Example:
        first page:
            http://www.quoka.de/immobilien/bueros-gewerbeflaechen/berlin/cat_27_2710_ct_111756.html
        second page:
            http://www.quoka.de/kleinanzeigen/cat_27_2710_ct_111756_page_2.html
        """

        # first page
        page_generator = self.parse_page(response)
        if page_generator:
            for item in page_generator:
                #print item
                yield item

        # next pages
        # calculate nof_pages because not all page links are in the html
        # This is necessary if there are more than 9 pages

        nof_pages = get_nof_pages(response)

        if nof_pages > 1:
            url_format = get_url_format(response)
            for page_nr in range(2, nof_pages + 1):
                url = url_format % page_nr
                yield scrapy.Request(url, self.parse_page, meta=response.meta, dont_filter=True)

    def parse_page(self, response):
        """crawl properties on a page"""

        # handle "Partner-Anzeigen"
        # need to identify correct css/xpath
        #print len(response.xpath("//div[text() = 'Partner-Anzeige']"))
        #print len(response.css("div #ResultListData > ul.alist > li[data-ssp]"))
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        for box in response.css("div #ResultListData > ul > li[data-ssp]"):
            loader = PropertyLoader(item=PropertyItem(), response=response)
            #loader.add_css("header", box.css("h3::text"))
            loader.add_value("advertiser_id", "Immobilienscout24")
            loader.add_value("commercial", response.meta.get("commercial"))
            loader.add_value("property_type", response.meta.get("property_type"))
            loader.add_value("city_category", response.meta.get("city_category"))  # stats

            item = loader.load_item()
            yield item

        # handle non-"Partner-Anzeigen"
        for sel in response.css("div #ResultListData > ul > li.hlisting  > div.n2 > a::attr(\"href\")"):
            url = add_scheme_host(sel.extract())
            yield scrapy.Request(url, self.parse_property, meta=response.meta)

    def parse_property(self, response):
        loader = PropertyLoader(item=PropertyItem(), response=response)

        loader.add_css("header", "div.headline > h2::text")
        loader.add_css("description", "div.text::text")
        loader.add_css("price", "div.price strong span::text")
        loader.add_css("postal_code", "div.location span.address span.postal-code::text")
        loader.add_css("city", "div.location span.address span.locality::text")
        loader.add_css("obid", "div.date-and-clicks > strong:nth-child(1)")
        loader.add_css("ad_created", "div.date-and-clicks::text")
        loader.add_css("phone", "ul.contacts > li > span:nth-child(2)::text")
        loader.add_value("created", date.today())
        loader.add_value("url", response.url)
        loader.add_value("commercial", response.meta.get("commercial"))
        loader.add_value("property_type", response.meta.get("property_type"))
        loader.add_value("city_category", response.meta.get("city_category"))  # stats

        item = loader.load_item()
        return item
