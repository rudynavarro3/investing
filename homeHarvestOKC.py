from homeharvest import scrape_property
from datetime import datetime
import pandas as pd

# Input Variables
radius = 100
# listing_type = "sold" # (sold, for_sale, for_rent, pending)
past_days = 360
# date_from="2023-05-01" # alternative to past_days 
# date_to="2023-05-28"
# mls_only=True  # only fetch MLS listings
# proxy="http://user:pass@host:port"  # use a proxy to change your IP address
# scrape_property(radius=radius, location="73003", listing_type=listing_type, past_days=past_days, mls_only=mls_only, proxy=proxy)

locations = ["Oklahoma City, OK", "Seward, OK", "Guthrie, OK", "Edmond, OK"]
for location in locations:
    if 'sold' not in locals():
        sold = scrape_property(radius=radius, location=location, listing_type="sold", past_days=past_days)
        print(f"Number of sold properties in {location}: {len(sold)}")
    else:
        df = scrape_property(radius=radius, location=location, listing_type="sold", past_days=past_days)
        print(f"Number of sold properties in {location}: {len(df)}")
        sold = pd.concat([sold,df])

    if 'selling' not in locals():
        selling = scrape_property(radius=radius, location=location, listing_type="for_sale", past_days=past_days)
        print(f"Number of selling properties in {location}: {len(selling)}")
    else:
        df = scrape_property(radius=radius, location=location, listing_type="for_sale", past_days=past_days)
        print(f"Number of selling properties in {location}: {len(df)}")
        selling = pd.concat([selling,df])

    if 'renting' not in locals():
        renting = scrape_property(radius=radius, location=location, listing_type="for_rent", past_days=past_days)
        print(f"Number of renting properties in {location}: {len(renting)}")
    else:
        df = scrape_property(radius=radius, location=location, listing_type="for_rent", past_days=past_days)
        print(f"Number of renting properties in {location}: {len(df)}")
        renting = pd.concat([renting,df])

    if 'pending' not in locals():
        pending = scrape_property(radius=radius, location=location, listing_type="pending", past_days=past_days)
        print(f"Number of pending properties in {location}: {len(pending)}")
    else:
        df = scrape_property(radius=radius, location=location, listing_type="pending", past_days=past_days)
        print(f"Number of pending properties in {location}: {len(df)}")
        pending = pd.concat([pending,df])

sold.to_csv(f"HomeHarvest_OKC_sold.csv", index=False)
selling.to_csv(f"HomeHarvest_OKC_selling.csv", index=False)
renting.to_csv(f"HomeHarvest_OKC_renting.csv", index=False)
pending.to_csv(f"HomeHarvest_OKC_pending.csv", index=False)
