import logging

import pandas as pd
from pytrends.request import TrendReq

# Configure logging
logging.basicConfig(
    filename="trending_searches.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

# Initialize pytrends
pytrends = TrendReq(hl="en-US", tz=360)


# Function to fetch trending searches
def fetch_trending_searches():
    try:
        logging.info("Fetching trending searches")
        trending_searches_df = pytrends.trending_searches(pn="united_states")
        logging.info("Trending searches fetched successfully")
        return trending_searches_df
    except Exception as e:
        logging.error("Error fetching trending searches: %s", e)
        return pd.DataFrame()


def main():
    try:
        # Fetch trending searches
        trending_searches_df = fetch_trending_searches()

        # Display the top 100 trending searches
        if not trending_searches_df.empty:
            top_100_trending_searches = trending_searches_df.head(100)
            print(top_100_trending_searches)
            logging.info("Top 100 trending searches displayed successfully")
        else:
            logging.info("No trending searches data available")
    except Exception as e:
        logging.error("Error in main script: %s", e)


# Main script
if __name__ == "__main__":
    main()
