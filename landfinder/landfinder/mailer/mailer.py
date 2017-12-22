import yagmail

# Need to connect to pymongo:
# - Find all entries of type "Landfinder" in the "listings_scraper_realestate_com_au" collection of "builteasy" database
# - For each entry found, check if the "Landmailer_%region%" entry exists in iterations[].mail[] set
# - If not, then update the field with an append and extract the html and append it to a dict containing the region
# - Send emails to all recipients with email subject title organized by region


def send_email(recipients, subject, html):
    yag = yagmail.SMTP(
        {'builteasyshortlister@gmail.com': 'Built Easy Shortlister'}, 'BuiltEasy123!')

    yag.send(to=recipients, subject=subject, contents=[html.replace('\n', '')])

