# import craigslistscraper as cs
# import pandas as pd
import csv
import json
import logging
import os
import sys

sys.path.insert(0, '/Users/rudy/CraigslistScraper')
import craigslistscraper as cs

# Setup Logger
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

# Define the search. Everything is done lazily, and so the html is not 
# fetched at this step.
search = cs.Search(
    query = "garage+sale",
    city = "oklahomacity",
    category = "sss"
)

# Define the filters
filters = {
    "postedToday": 0,
    "bundleDuplicates": 1,
    "max_price": 100000
}

# Fetch the html from the server. Don't forget to check the status. Notice that
# the filters are passed in through the requests.get(params = ...) argument.
status = search.fetch(params = filters)
if status != 200:
    raise Exception(f"Unable to fetch search with status <{status}>.")

logging.info(f"{len(search.ads)} ads found from {search.url}")
idx, data = 0, []
columns = set()
for raw_listing in search.ads:
    status = raw_listing.fetch()
    try:
        status = raw_listing.fetch()
    except Exception as e:
        logging.error(f"{raw_listing.url} --> {e}")
        continue
    
    if status != 200:
        logging.error(f"Unable to fetch ad '{raw_listing.title}' with status <{status}>.")
        continue
    else:
        listing = raw_listing.to_dict()
        
        data.append(listing)

        columns.update(set(listing.keys()))

        # json.dumps is merely for pretty printing. 
        logging.debug(json.dumps(listing, indent = 4))

    idx += 1
    if idx >= 30:
        break

# Export to dataset
with open("cl_listings.json", "w") as file:
    json.dump(data, file)
# csv_columns = list(columns)
# with open('cl_listings.csv', 'a') as f:
#     wr = csv.DictWriter(f, fieldnames=csv_columns, delimiter='\t')
#     wr.writeheader()
#     wr.writerows(data)
    
# data = pd.read_json(path_to_input_file)
# data.to_csv(path_to_csv_output_file)