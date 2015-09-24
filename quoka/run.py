

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from quoka.spiders.properties import PropertiesSpider
from quoka.storage import prepare_database

# before running the script
# export PYTHONPATH=$PWD

# setup db
prepare_database()


process = CrawlerProcess(get_project_settings())
process.crawl(PropertiesSpider)
process.start()
