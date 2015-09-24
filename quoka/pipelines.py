# -*- coding: utf-8 -*-


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import MySQLdb as mdb

from quoka.storage import get_connection

class StatsPipeline(object):

    def __init__(self):
        self.con = get_connection("crawl")
        self.cur = self.con.cursor()

    def process_item(self, item, spider):

        params = (
            item.get("commercial"),
            item.get("city_category")
        )
        try:
            self.cur.execute(
                """
                INSERT INTO stats (
                    commercial,
                    city_category
                ) VALUES (
                    %s, %s
                )

                """,
                params
            )
            self.con.commit()
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return item


class MySQLStoragePipeline(object):

    def __init__(self):
        self.con = get_connection("crawl")
        self.cur = self.con.cursor()

    def process_item(self, item, spider):

        params = (
            item.get("header"),
            item.get("description"),
            item.get("price"),
            item.get("postal_code"),
            item.get("city"),
            item.get("obid"),
            item.get("ad_created"),
            item.get("phone"),
            item.get("created"),
            item.get("url"),
            item.get("commercial"),
            item.get("advertiser_id"),
            item.get("property_type")
        )

        try:
            self.cur.execute(
                """
                INSERT INTO quoka (
                    Überschrift,
                    Beschreibung,
                    Kaufpreis,
                    PLZ,
                    Stadt,
                    OBID,
                    Erstellungsdatum,
                    Telefon,
                    erzeugt_am,
                    url,
                    Gewerblich,
                    Anbieter_Id,
                    Immobilientyp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )

                """,
                params
            )
            self.con.commit()
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return item
