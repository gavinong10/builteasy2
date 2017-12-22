# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import boto3
import datetime
from pytz import timezone
import pymongo
from pymodm import connect
from schemas import ListingResult, Listing
class LandfinderPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE', 'items'),
        )

    def open_spider(self, spider):
        # self.client = pymongo.MongoClient(self.mongo_uri)
        # self.db = self.client[self.mongo_db]
        self.scraper_type = spider.name
        connect(self.mongo_uri + '/' + self.mongo_db)

    def close_spider(self, spider):
        pass
        # self.client.close()

    def process_item(self, item, spider):
        # Query for the URL and obtain a list of the versions.abs
        # Compare the newest version's HTML to the current one. 
        # If different or non-existent, then put/update the entry with a new version entry.
        # A version entry has fields: date_discovered, listing_html, listing_name, mail, version_no

        # Mail is used to track which mailing lists have already sent emails for the discovered listing.
        
        #### START MONGODB ####
        # TODO: Incorporate $currentDate	
        
        index = {
            'listing_url': item["listing_url"],
            'search_id': self.scraper_type
        }

        listingRes = ListingResult(
            date_discovered=datetime.datetime.now(
                timezone("Australia/Brisbane")),
            listing_name=item["listing_name"],
            listing_html=item["listing_html"]
        )
        
        try:
            listing = Listing.objects.get(index)

            # Check if html has changed
            if listing["iterations"][-1]["listing_html"] != item["listing_html"]:
                #iterations
                listing.update(
                    index,
                    {'$push': listingRes }
                )

            # If yes, then do a 
        except Listing.DoesNotExist:
            # Handle Listing not existing.
            Listing(
                listing_url=item["listing_url"],
                search_id=self.scraper_type,
                iterations=[listingRes]
            ).save()
    
    