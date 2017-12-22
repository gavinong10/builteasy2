from collections import OrderedDict
import urllib
import scrapy
from landfinder.items import LandfinderItem
import pandas as pd
import os

# https://www.realestate.com.au/buy/property-land-in-kuraby%2c+qld+4112/list-1?includeSurrounding=false&persistIncludeSurrounding=true&misc=ex-under-contract&source=location-search
# https://www.realestate.com.au/buy/property-land-in-pimpama,+qld+4209/list-1?activeSort=list-date&misc=ex-under-contract&includeSurrounding=false
# https://www.realestate.com.au/buy/property-land-in-pimpama,+qld+4209/list-2?activeSort=list-date&misc=ex-under-contract&includeSurrounding=false

def read_df(): #TODO
    dir_path = os.path.dirname(os.path.realpath(__file__))
    df = pd.read_csv(dir_path + "/inputs/landsearchlist.csv")
    print df.head()
    return df

def preprocess_df(df):
    df["Suburb"] = df["Suburb"].astype(str).apply(
        lambda suburb: suburb.lower().replace(" ", "+"))
    df["State"] = df["State"].astype(str).apply(lambda state: state.lower())
    df["Postcode"] = df["Postcode"].astype(str)

df = read_df()
preprocess_df(df)

params = {
    'activeSort': 'list-date',
    'misc': 'ex-under-contract',
    'includeSurrounding': 'false'
}
params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
params = urllib.urlencode(params)

class LandListingsSpider(scrapy.Spider):
    name = "Landfinder"
    page = 1
    start_urls = ["https://www.realestate.com.au/buy/property-land-in-%s%%2c+%s+%s%%3b/list-%d?%s" % (row["Suburb"], row["State"], row["Postcode"], page, params) for _, row in df.iterrows()]

    custom_settings = {
        'MONGODB_URI': 'mongodb://localhost:27017',
        'MONGODB_DATABASE': 'builteasy'
    }
    
    def parse(self, response):
        listings = response.xpath(
            "//*[@id='searchResultsTbl']//*[contains(@class, 'listingInfo')]")

        listing_names = listings.xpath("//*[@rel='listingName']/text()").extract()
        listing_urls = listings.xpath(
                    "//*[@rel='listingName']/@href").extract()
        listing_htmls = listings.xpath(
                    "//*[@rel='listingName']//ancestor::article").extract()

        for i in range(len(listings)):
            item = LandfinderItem(
                listing_name=listing_names[i],
                listing_url=listing_urls[i],
                listing_html=listing_htmls[i],
            )
            yield item

        next_page=response.xpath(
                    "//*[contains(@class, 'nextLink')]//a/@href").extract_first()

        # TODO: Only if database doesn't contain it
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
