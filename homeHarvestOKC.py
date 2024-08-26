# from datetime import datetime

import pandas as pd
from homeharvest import scrape_property

# Input Variables
radius = 100
# listing_type = "sold" # (sold, for_sale, for_rent, pending)
# past_days = 720
# date_from="2022-01-01" # alternative to past_days
# date_to=datetime.now().strftime('%Y-%m-%d')
# mls_only=True  # only fetch MLS listings
# proxy="http://user:pass@host:port"  # use a proxy to change your IP address
# scrape_property(radius=radius, location="73003", listing_type=listing_type, past_days=past_days, mls_only=mls_only, proxy=proxy)

update_historical = True
# years = ["2020" "2021", "2022", "2023", "2024"]
years = ["2022", "2023", "2024"]
# years = ['2024']
for idx, year in enumerate(years):
    date_from = f"{year}-01-01"  # alternative to past_days
    date_to = f"{year}-12-31"
    location_prefix = "OKC"
    locations = [
        "Oklahoma City, OK",
        "Seward, OK",
        "Guthrie, OK",
        "Edmond, OK",
        "Norman, OK",
        "Moore, OK",
        "Yukon, OK",
        "Perry, OK",
        "Stillwater, OK",
        "Perkins, OK",
        "Langston, OK",
        "Hennessey, OK",
        "Kingfisher, OK",
    ]
    for location in locations:
        if update_historical:
            if "sold" not in locals():
                sold = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="sold",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of sold properties in {location}: {len(sold)}")
            else:
                df = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="sold",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of sold properties in {location}: {len(df)}")
                sold = pd.concat([sold, df])
        if year == years[-1]:
            if "selling" not in locals():
                selling = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="for_sale",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of selling properties in {location}: {len(selling)}")
            else:
                df = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="for_sale",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of selling properties in {location}: {len(df)}")
                selling = pd.concat([selling, df])

            if "renting" not in locals():
                renting = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="for_rent",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of renting properties in {location}: {len(renting)}")
            else:
                df = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="for_rent",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of renting properties in {location}: {len(df)}")
                renting = pd.concat([renting, df])

            if "pending" not in locals():
                pending = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="pending",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of pending properties in {location}: {len(pending)}")
            else:
                df = scrape_property(
                    radius=radius,
                    location=location,
                    listing_type="pending",
                    date_from=date_from,
                    date_to=date_to,
                )
                print(f"Number of pending properties in {location}: {len(df)}")
                pending = pd.concat([pending, df])

    if update_historical:
        sold.to_csv(
            f"data/homeHarvest/HomeHarvest_{location_prefix}_{year}_sold.csv",
            index=False,
        )
        del sold

    if idx == len(years) - 1:
        selling.to_csv(
            f"data/homeHarvest/HomeHarvest_{location_prefix}_selling.csv", index=False
        )
        renting.to_csv(
            f"data/homeHarvest/HomeHarvest_{location_prefix}_renting.csv", index=False
        )
        pending.to_csv(
            f"data/homeHarvest/HomeHarvest_{location_prefix}_pending.csv", index=False
        )
