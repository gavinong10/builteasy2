# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class LandfinderItem(scrapy.Item):
    listing_name = scrapy.Field()
    listing_url = scrapy.Field()
    listing_html = scrapy.Field()
    search_url = scrapy.Field()
    postcode = scrapy.Field()
