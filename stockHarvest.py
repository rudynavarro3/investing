"""
stockHarvest.py ~ scrape macrotrends for basic stock metrics

Prerequisites:
    pip install yahoofinancials yahoo-finance yahoo_fin selenium requests_html lxml
    conda activate ds

Setup Safari:
    - open safari
    - Open safari settings -> advanced tab
    - Check the "Show features for Web developers" checkbox

    then

    - From the new 'Develop' tab in the top ribbon, click "developer settings"
    - Check the "Allow remote automation" checkbox

Recommended python version 3.8.18
"""
from yahoofinancials import YahooFinancials
import yahoo_fin.stock_info as si
import pandas as pd
import logging
import time
import json
from io import StringIO
from selenium import webdriver
from datetime import datetime

# Setup Logger
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# https://medium.com/jpa-quant-articles/stock-valuation-in-python-phil-town-intrinsic-value-2306b32cea9d

datestr = datetime.now().strftime('%Y-%m-%d')

def analyze_town(ticker:str=None, name:str='') -> float:
    ticker = ticker.upper()
    name = name.lower()

    url = f'https://www.macrotrends.net/stocks/charts/{ticker}/{name}/pe-ratio'

    try:
        driver = webdriver.Safari()
        driver.get(url)
        time.sleep(1)
        sdata = pd.read_html(StringIO(str(driver.page_source)))[0]

        logging.debug(sdata.head())

        sdata.columns = sdata.columns.droplevel(0) # Get rid of the 'super' header
        sdata.rename(columns={
                list(sdata)[0]:'Year', 
                list(sdata)[1]:'Price', 
                list(sdata)[2]:'EPS', 
                list(sdata)[3]:'PE'
            }, inplace=True) # Rename columns
        logging.debug(sdata.head())

        # stock_obj = YahooFinancials(ticker)
        # eps = stock_obj.get_earnings_per_share()
        # current_price = stock_obj.get_current_price()

        eps = float(sdata['EPS'][sdata['EPS'].notna().idxmax()].replace('$',''))
        current_price = sdata['Price'][0]

        cagr = si.get_analysts_info(ticker)['Growth Estimates'][ticker][4]
        cagr = float(cagr.replace('%','')) / 100 # convert to percentage
        logging.debug(f"-->{ticker}<-- cagr={cagr}")

        pe1 = float(2 * 100 * cagr) # mulitply by 2
        pe2 = float(sdata['PE'].iloc[0:20].mean()) # get the mean of the CAGR
        pe = min(pe1, pe2)
        logging.debug(f"-->{ticker}<-- pe={pe}")

        earnings_dict = {0:round(eps,2)}
        logging.debug(f"earnings_dict={earnings_dict}")

        for i in range(1,10):
            earnings_dict[i] = round(earnings_dict[i-1]+(earnings_dict[i-1] * cagr),2)

        logging.debug(f"-->{ticker}<-- earnings_dict={earnings_dict}")

        fair_price_dict = {9: earnings_dict[9]*pe}
            
        for i in range(8,-1,-1):
            fair_price_dict[i] = fair_price_dict[i+1]/(1+0.15)
        logging.debug(f"-->{ticker}<-- fair_price_dict={fair_price_dict}")

        current_fair_price = round(fair_price_dict[0],2)
        logging.debug(f"-->{ticker}<-- current_fair_price={current_fair_price}")

        buyable_price = round((current_fair_price * 0.5), 2)
        logging.debug(f"-->{ticker}<-- buyable_price={buyable_price}")

        buy_ratio = buyable_price/current_price
        logging.debug(f"-->{ticker}<-- buy_ratio={buy_ratio}")

        figures = {
            'date': datestr,
            'symbol': ticker,
            'EPS': round(eps,6),
            'CAGR': round(cagr,6),
            'PE_val': round(pe,6),
            'PE_avg': round(pe1,6),
            'current_price': round(current_price,6),
            'current_fair_price': round(current_fair_price,6),
            'buy_ratio': round(buy_ratio,6)
        }
    except:
        # logging.error(f"Could not process {ticker}")
        figures = {
            'date': datestr,
            'symbol': ticker,
            'EPS': '',
            'CAGR': '',
            'PE_val': '',
            'PE_avg': '',
            'current_price': '',
            'current_fair_price': '',
            'buy_ratio': 0.
        }
    finally:
        try:
            driver.close()
        except:
            logging.debug('pass')

    return figures

def get_tickers():
    df1 = pd.read_csv('stock_info.csv')
    tickers = set(df1["Ticker"].values.tolist())

    df2 = pd.read_csv('nasdaq-listed.csv')
    tickers.update(set(df2["Symbol"].values.tolist()))

    mag7 = ['AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA']
    tickers.update(set(mag7))

    ticker_list = list(tickers)
    ticker_list.sort()

    return ticker_list

if __name__ == '__main__':
    tickers = get_tickers()
    # tickers = ['AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA']

    complete_list = []
    for ticker in tickers:
        # logging.info(f"Processing {ticker}...")
        figures = analyze_town(ticker=ticker)
        complete_list.append(figures)
        buy_ratio = figures['buy_ratio']
        if buy_ratio > 0.7:
            logging.info(f" >>>>>>>>>>>>>> BUY {ticker} --> buy_ratio={buy_ratio}")
        elif buy_ratio > 0.0:
            logging.info(f" {ticker} --> buy_ratio={buy_ratio}")

    export_file = f'data/stockHarvest/stockHarvest_value_analysis_{datestr}.csv'
    pd.DataFrame(complete_list).to_csv(export_file, index=False)
