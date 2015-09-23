# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from datetime import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst


class PropertyLoader(ItemLoader):

    default_output_processor = TakeFirst()


def trim(string):
    result = string.strip()
    if result:
        return result
    return None

def only_digits(string):
    result = re.sub("\D", "", string)
    return result


def parse_date(string):
    string = string.strip()

    try:
        date_object = datetime.strptime(string, '%d.%m.%Y')
        return date_object
        #return datetime.strftime(date_object, "%Y-%m-%d")

    except ValueError:
        return None



class PropertyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    header = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(only_digits))
    postal_code = scrapy.Field()
    city = scrapy.Field()
    obid = scrapy.Field()
    ad_created = scrapy.Field(input_processor=MapCompose(trim, parse_date))
    phone = scrapy.Field()
    created = scrapy.Field()
    url = scrapy.Field()
    commercial = scrapy.Field()
    advertiser_id = scrapy.Field()
