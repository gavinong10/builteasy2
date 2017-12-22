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

# session = boto3.session.Session(
#     profile_name='builteasy', region_name='us-west-2')

# # Get the service resource.
# dynamodb = session.resource('dynamodb')

# table = dynamodb.Table('ListingExp0')

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
        connect('mongodb://' + self.mongo_uri + '/' + self.mongo_db)

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
        try:
            listing = Listing.objects.get({
                'listing_url': item["listing_url"],
                'search_id': self.scraper_type
                })

            # Check if html has changed
            if listing["iterations"][-1]["listing_html"] != item["listing_html"]:
                listing.update(
                    { TODO }
                )

            # If yes, then do a 
        except Listing.DoesNotExist:
            # Handle Listing not existing.
            pass
    



# if (myDocument) {
#    var oldQuantity = myDocument.quantity
#    var oldReordered = myDocument.reordered

#    var results = db.products.update(
#        {
#            _id: myDocument._id,
#            quantity: oldQuantity,
#            reordered: oldReordered
#        },
#        {$inc: {quantity: 50},
#         $set: {reordered: true}
#         }
#    )

#    if (results.hasWriteError()) {
#        print("unexpected error updating document: " + tojson(results))
#    }
#     else if (results.nMatched == = 0) {
#        print("No matching document for " +
#              "{ _id: " + myDocument._id.toString() +
#              ", quantity: " + oldQuantity +
#              ", reordered: " + oldReordered
#              + " } "
#              )
#    }
#    }



        stored_item = self.db[self.COLLECTION_NAME].get(query)

        if stored_item is None:
            self.db[self.COLLECTION_NAME].insert_one(
                dict(query.items() + {
                    "iterations": [{
                        "data_discovered_int": int(datetime.datetime.now(
                            timezone("Australia/Brisbane")).strftime("%Y%m%d%H%S")),
                        "date_discovered": datetime.datetime.now(
                            timezone("Australia/Brisbane")),
                        "listing_html": item["listing_html"],
                        "   listing_name": item["listing_name"],
                        "version": 0,
                        "mail": [],
                    }]
                }.items())
            )
        else:
            if stored_item["iterations"][-1]["listing_html"] != item["listing_html"]:
                stored_item["iterations"].push({
                    "data_discovered_int": int(datetime.datetime.now(
                        timezone("Australia/Brisbane")).strftime("%Y%m%d%H%S")),
                    "date_discovered": datetime.datetime.now(
                        timezone("Australia/Brisbane")),
                    "listing_html": item["listing_html"],
                    "listing_name": item["listing_name"],
                    "version": len(stored_item["Iterations"]),
                    "mail": [],
                })
                self.db[self.COLLECTION_NAME].replace_one(
                    query,
                    stored_item)

        return item
