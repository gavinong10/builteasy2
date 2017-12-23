import yagmail
from settings import MONGODB_URI, MONGODB_DATABASE
from pymodm import connect
from schemas import ListingResult, Listing, ListingId
import pandas as pd
import os
from bson.son import SON
import pymongo

#__file__ = "/Users/macbook/Development/builteasy/landfinder/landfinder/mailer/mailer.py"; execfile(__file__)

# Need to connect to pymongo:
# - Find all entries of type "Landfinder" in the "listings_realestate_com_au" collection of "builteasy" database
# - For each entry found, check if the "Landmailer_%region%" entry exists in iterations[].mail[] set
# - If not, then update the field with an append and extract the html and append it to a dict containing the region
# - Send emails to all recipients with email subject title organized by region

RECIPIENTS = ["gavin.ong@builteasy.com.au"] #, "morgan@builteasy.com.au", "miran@builteasy.com.au", "gavin@builteasy.com.au"]

from pymongo import MongoClient
client = MongoClient(MONGODB_URI + '/')
db = client[MONGODB_DATABASE]
collection = db[Listing.Meta.collection_name]
res_collection = db[ListingResult.Meta.collection_name]

def read_landsearchlist_df():  # TODO
    dir_path = os.path.dirname(os.path.realpath(__file__))
    landsearchlist_df = pd.read_csv(dir_path + "/../inputs/landsearchlist.csv")
    return landsearchlist_df

def get_results(objectids):
    return res_collection.find({ "_id": {'$in': objectids}})

def extract_entries_for_region(region, group, mailer):
    # Execute a query that finds all the entries corresponding to postcode
    # And is missing the relevant mail reference
    
    mongo_entries = collection.find(
        {
            Listing._id.mongo_name + '.' + ListingId.search_id.mongo_name: "Landfinder",

        })

    eligible_postcodes = list(group["Postcode"].astype(str))
    print eligible_postcodes

    pipeline = [
        {
            '$match': {
                '$and': [
                    {
                        Listing._id.mongo_name + '.' + ListingId.search_id.mongo_name: "Landfinder",
                    },
                    {
                        Listing.postcode.mongo_name: {'$in': eligible_postcodes}
                    }
                ] 
            },  
        },
    ]

    mongo_entries = collection.aggregate(pipeline)
    return mongo_entries


def generate_html(mongo_entries, mailer):
    # Loop through each mongo entry and check all entries that don't have the mailer
    # Pull out the corresponding listing_name, date_discovered and listing_html
    listing_names = []
    date_discovereds = []
    listing_htmls = []
    
    affected_entries = []

    
    for entry in mongo_entries:
        print "entry: ", entry
        print "iterations: ", list(get_results(entry["iterations"]))
        unmailed_iterations = [
            iteration for iteration in get_results(entry["iterations"]) if  mailer_name not in iteration.get("mail", [])
        ]
        for iteration in unmailed_iterations:
            print "\n\niteration: ", iteration
            affected_entries += unmailed_iterations
            listing_names.append(iteration["listing_name"])
            # TODO: format to Brisbane time
            date_discovereds.append(iteration["date_discovered"])
            listing_htmls.append(iteration["listing_html"])
    
    # TODO: Generate the html email in jinja2
    email_html = "<br />\n<p>##############</p><br />".join(listing_htmls)
    email_html.replace('href="/', 'href="http://www.realestate.com.au/'

    # zip(listing_names, date_discovereds, listing_htmls)
    return email_html, affected_entries


def update_db(changed_result_entries, mailer):
    # For each of the entries, update the 'mail' set to include this mailer
    for entry in changed_result_entries:
        entry["mail"] = entry.get("mail", []) + [mailer]
        ListingResult(**{ k: entry[k] for k in entry.keys() if k == '_id' or (k[0] != "_")}).save()

def send_email(recipients, subject, html):
    yag = yagmail.SMTP(
        {'builteasyshortlister@gmail.com': 'Built Easy Shortlister'}, 'BuiltEasy123!')

    yag.send(to=recipients, subject=subject, contents=[html.replace('\n', '')])

connect(MONGODB_URI + '/' + MONGODB_DATABASE)
landsearchlist_df = read_landsearchlist_df()

for region, group in landsearchlist_df.groupby('Region'):
    mailer_name = region + ' - landmailer'
    mongo_entries = extract_entries_for_region(region, group, mailer_name)
    html, changed_result_entries = generate_html(mongo_entries, mailer_name)
    if len(changed_result_entries) > 0:
        send_email(RECIPIENTS, mailer_name, html)
        update_db(changed_result_entries, mailer_name)

