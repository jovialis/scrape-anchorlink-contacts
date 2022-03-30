import json
import random
from pprint import pprint
import requests
import os
import time
from dotenv import load_dotenv

# Loads the cookie and header token from .env file
load_dotenv()

# Authorization headers to use
headers = {
    "cookie": os.getenv('COOKIE'),
    "x-xsrf-token": os.getenv('XSRF-TOKEN')
}

# Fetches all of the student Organizations or loads from file
if os.path.exists('all_anchorlink_orgs.json'):
    parsed = json.load(open('all_anchorlink_orgs.json', 'r'))
    print("Loaded {} organizations from file.".format(len(parsed['value'])))
else:
    #
    res = requests.get(
        f'https://anchorlink.vanderbilt.edu/api/discovery/search/organizations?top=5000&filter=&query=&skip=0',
        headers=headers
    )

    parsed = res.json()
    json.dump(parsed, open('all_anchorlink_orgs.json', 'w'))

    print("Collected {} organizations".format(len(parsed['value'])))


org_ids = [x["WebsiteKey"] for x in parsed["value"]]

if os.path.exists('output.json'):
    org_details = json.load(open('output.json', 'r'))
else:
    org_details = {}

retry = 0

# Iterates over all organizations, fetching Organization data for each
for oid in org_ids:
    if retry > 5:
        print("Max retries exceeded. Erroring out.")
        break

    if oid in org_details:
        print('Skipping {}'.format(oid))
        continue

    try:
        # print("Attempting to scrape {}".format(oid))

        res = requests.get(
            f'https://anchorlink.vanderbilt.edu/api/discovery/organization/bykey/{oid}',
            headers=headers
        )

        org_details[oid] = res.json()
        time.sleep(random.random())

        print(f"Scraped {oid}")
        retry = 0
        # break
    except Exception as e:
        if str(e).startswith("Expecting value"):
            print("Failed to parse JSON result for {}. Skipping!".format(oid))
            continue
        else:
            print("Failed query. Retrying!")
            retry += 1
            print(e)

# Print all data and output it
pprint(org_details)
json.dump(org_details, open('output.json', 'w'))

all_orgs = json.load(open('output.json', 'r'))
primary_contacts = [{
    "organization": x["name"],
    "status": x["status"],
    "admin": x["isAdminOnly"],
    "contact": None if not x["primaryContact"] else {
        "first": x["primaryContact"]["preferredFirstName"] or x["primaryContact"]["firstName"],
        "last": x["primaryContact"]["lastName"],
        "email": x["primaryContact"]["primaryEmailAddress"]
    }
} for x in all_orgs.values()]

primary_contacts = filter(lambda x: x["status"] == "Active" and x["admin"] is not True, primary_contacts)

# Output dataset as a CSV/Pandas dataframe
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', 0)

df = pd.DataFrame(primary_contacts)
contact_df = pd.json_normalize(df["contact"])

df["contact.first"] = contact_df["first"]
df["contact.last"] = contact_df["last"]
df["contact.email"] = contact_df["email"]

df = df.drop(columns=["status", "admin", "contact"])

df.to_csv('representatives.csv', index_label=False, index=False)

pprint(df)
