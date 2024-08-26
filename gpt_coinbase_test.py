import logging
import os
import time

import pandas as pd
from coinbase.wallet.client import Client

# Replace with your Coinbase API credentials
API_KEY = os.environ.get("coinbase_test_api_key")
API_SECRET = os.environ.get("coinbase_test_api_secret")
client = Client(API_KEY, API_SECRET)

# Initial investment
investment_amount = 100.0


# Define a function to get the current price of a cryptocurrency
def get_current_price(currency_pair):
    price = client.get_spot_price(currency_pair=currency_pair)
    return float(price["amount"])


# Define a function to calculate potential profit after fees and taxes
def calculate_profit(
    buy_price, sell_price, amount, fee_percentage=0.5, tax_percentage=15
):
    trading_fee = fee_percentage / 100
    capital_gains_tax = tax_percentage / 100

    gross_profit = (sell_price - buy_price) * amount
    net_profit = (
        gross_profit - (gross_profit * trading_fee) - (gross_profit * capital_gains_tax)
    )

    return net_profit


# Define a function to decide whether to trade
def should_trade(buy_price, current_price, amount, target_profit_percentage=5):
    target_profit = amount * target_profit_percentage / 100
    net_profit = calculate_profit(buy_price, current_price, amount)

    return net_profit >= target_profit


# Main trading loop
def trade_bot():
    global investment_amount
    buy_price = get_current_price("BTC-USD")
    amount_invested = investment_amount / buy_price
    print(f"Bought BTC at ${buy_price:.2f}, amount: {amount_invested:.6f} BTC")

    while True:
        current_price = get_current_price("BTC-USD")
        if should_trade(buy_price, current_price, amount_invested):
            investment_amount = current_price * amount_invested
            print(
                f"Sold BTC at ${current_price:.2f}, new investment amount: ${investment_amount:.2f}"
            )
            buy_price = current_price
            amount_invested = investment_amount / buy_price
            print(f"Bought BTC at ${buy_price:.2f}, amount: {amount_invested:.6f} BTC")

        time.sleep(30)


# Start the trading bot
if __name__ == "__main__":
    trade_bot()
