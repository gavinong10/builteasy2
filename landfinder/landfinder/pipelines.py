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
from schemas import ListingId, ListingResult, Listing
import re
class LandfinderPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @staticmethod
    def censor_html_links(html):
        return re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", html)

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
            '_id': {
                'listing_url': item["listing_url"],
                'search_id': self.scraper_type
            }
        }
        listingId = ListingId(
            **index["_id"]
        )

        listingRes = ListingResult(
            date_discovered=datetime.datetime.now(
                timezone("Australia/Brisbane")),
            listing_name=item["listing_name"],
            listing_html=item["listing_html"],
            search_url=item["search_url"]
        )
        
        try:
            listing = Listing.objects.get(index)
            # print "#########"
            # print listing.iterations
            # exit(1)
            # Check if html has changed

            censored_html_iterations = [self.censor_html_links(
                iteration.listing_html) for iteration in listing.iterations]

            if self.censor_html_links(item["listing_html"]) not in censored_html_iterations:
                listingRes.save()
                Listing.objects.raw(index).update({
                    "$addToSet": {
                        "iterations": listingRes._id
                    }
                })

            # If yes, then do a 
        except Listing.DoesNotExist:
            # Handle Listing not existing.
            listingRes.save()
            Listing(
                _id=listingId,
                iterations=[listingRes],
                postcode=item["postcode"]
            ).save()
    
