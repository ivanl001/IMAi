# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AirApiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class City(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
