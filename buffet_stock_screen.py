import logging
import multiprocessing
import os
import time
from datetime import datetime
from multiprocessing import Pool

import pandas as pd
import yfinance as yf

# Constants for caching
CACHE_FILE = "tickers_cache.csv"


# Step 1: Fetch and Cache All Available Tickers
def fetch_all_tickers():
    if os.path.exists(CACHE_FILE):
        print("Loading cached tickers...")
        cached_tickers = pd.read_csv(CACHE_FILE)
        return cached_tickers["Symbol"].tolist()

    print("Fetching tickers from exchanges...")
    urls = {
        "NYSE": "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv",
        "https://datahub.io/core/nasdaq-listings/_r/-/data/nasdaq-listed-symbols.csv",
        # "NASDAQ": "https://old.nasdaq.com/screening/companies-by-name.aspx?exchange=NASDAQ&render=download",
        # "AMEX": "https://old.nasdaq.com/screening/companies-by-name.aspx?exchange=AMEX&render=download",
    }

    tickers = set()

    for exchange, url in urls.items():
        try:
            data = pd.read_csv(url)
            tickers.update(data["Symbol"].tolist())
        except Exception as e:
            print(f"Error fetching data from {exchange}: {e}")

    # Clean and save tickers
    tickers = [
        ticker.replace(".", "-") for ticker in tickers if isinstance(ticker, str)
    ]
    pd.DataFrame(tickers, columns=["Symbol"]).to_csv(CACHE_FILE, index=False)

    return tickers


# Step 2: Analyze Each Stock Based on Buffett's Principles
def analyze_stock(ticker):
    ref_date = datetime.today().strftime("%Y-%m-%d")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        pe_ratio = info.get("trailingPE", 0)
        roe = info.get("returnOnEquity", 0)
        debt_to_equity = info.get("debtToEquity", 0)
        profit_margin = info.get("profitMargins", 0)
        market_cap = info.get("marketCap", 0)

        # Score based on Buffett's criteria
        score = 0
        bin_score = []
        if pe_ratio and 0 < pe_ratio < 20:
            score += 1  # Undervalued
            bin_score.append("1")
        else:
            bin_score.append("0")

        if roe and roe > 0.15:
            score += 1  # High ROE
            bin_score.append("1")
        else:
            bin_score.append("0")

        if debt_to_equity and debt_to_equity < 0.5:
            score += 1  # Low Debt
            bin_score.append("1")
        else:
            bin_score.append("0")

        if profit_margin and profit_margin > 0.15:
            score += 1  # Strong Profitability
            bin_score.append("1")
        else:
            bin_score.append("0")

        if market_cap and market_cap > 10e9:
            score += 1  # Large, established company
            bin_score.append("1")
        else:
            bin_score.append("0")

        om_score = int("".join(bin_score[::-1]), 2)

        return {
            "Ticker": ticker,
            "ref_date": ref_date,
            "PE Ratio": pe_ratio,
            "ROE": roe,
            "Debt/Equity": debt_to_equity,
            "Profit Margin": profit_margin,
            "Market Cap": market_cap,
            "Score": score,
            "Weighted_Score": om_score,
        }
    except:
        return None


# Step 3: Parallel Analysis with Multiprocessing
def parallel_analysis(tickers, num_workers=4):
    print(f"Analyzing {len(tickers)} stocks using {num_workers} processes...")
    with Pool(processes=num_workers) as pool:
        results = pool.map(analyze_stock, tickers)
    return [res for res in results if res]  # Filter out None results


# Step 4: Main Execution Function
def main():
    start_time = time.time()

    # Fetch or load tickers
    tickers = fetch_all_tickers()
    print(f"Total tickers to analyze: {len(tickers)}")

    # Use all available CPU cores for multiprocessing
    num_cores = multiprocessing.cpu_count()
    analysis_results = parallel_analysis(
        tickers[:1000], num_workers=num_cores
    )  # Limit to 1000 for speed

    # Create DataFrame and sort by Score
    df = pd.DataFrame(analysis_results)
    top_stocks = df.sort_values(by="Score", ascending=False).head(10)

    print("\n📊 Top 10 Stocks Based on Warren Buffett's Principles:")
    print(
        top_stocks[
            [
                "Ticker",
                "ref_date",
                "PE Ratio",
                "ROE",
                "Debt/Equity",
                "Profit Margin",
                "Market Cap",
                "Score",
                "Weighted_Score",
            ]
        ]
    )

    # Save results
    df.to_csv("buffett_analysis_results.csv", index=False)

    elapsed_time = time.time() - start_time
    print(f"\n⏱️ Analysis completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
