import datetime as dt
import logging
import os

import numpy as np

# import pandas as pd
import requests
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Function to fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date, end=end_date)
    return hist


# Function to fetch news sentiment
def fetch_fmp_sentiment(
    api_key: str = os.environ["fmp_api_key"],
    query: str = None,
    period: str = "quarter",
):
    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{query}?period={period}&apikey={api_key}"
    response = requests.get(url).json()
    articles = response.get("articles", [])
    analyzer = SentimentIntensityAnalyzer()
    sentiments = [
        analyzer.polarity_scores(article["title"])["compound"] for article in articles
    ]
    avg_sentiment = np.mean(sentiments) if sentiments else 0
    return avg_sentiment


# # Function to fetch news sentiment
# def fetch_news_sentiment(api_key, query, from_date, to_date):
#     url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&sortBy=publishedAt&apiKey={api_key}"
#     response = requests.get(url).json()
#     articles = response.get("articles", [])
#     analyzer = SentimentIntensityAnalyzer()
#     sentiments = [
#         analyzer.polarity_scores(article["title"])["compound"] for article in articles
#     ]
#     avg_sentiment = np.mean(sentiments) if sentiments else 0
#     return avg_sentiment


# Preprocess the data
def preprocess_data(stock_data, sentiment_data):
    stock_data["Sentiment"] = sentiment_data
    stock_data = stock_data.dropna()
    return stock_data


# Create dataset for LSTM
def create_dataset(data, time_step=1):
    X, Y = [], []
    for i in range(len(data) - time_step - 1):
        X.append(data[i : (i + time_step), :])
        Y.append(data[i + time_step, 0])
    return np.array(X), np.array(Y)


# Build LSTM model
def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def main(
    ticker: str = "AAPL", start_date: str = "2023-07-06", end_date: str = "2024-07-25"
):

    # news_api_key = os.environ.get('news_api_key')

    # Fetch stock data
    stock_data = fetch_stock_data(ticker, start_date, end_date)

    # Fetch news sentiment data
    sentiment_data = []
    for date in stock_data.index:
        # sentiment = fetch_news_sentiment(
        #     news_api_key, ticker, date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")
        # )
        sentiment = fetch_fmp_sentiment(query=ticker, period="quarter")
        sentiment_data.append(sentiment)

    # Preprocess data
    stock_data["Sentiment"] = sentiment_data
    data = stock_data[["Close", "Volume", "Sentiment"]].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Create dataset for LSTM
    time_step = 60
    X, Y = create_dataset(scaled_data, time_step)
    X = X.reshape(X.shape[0], X.shape[1], X.shape[2])

    # Build and train the model
    model = build_lstm_model((X.shape[1], X.shape[2]))
    model.fit(X, Y, batch_size=32, epochs=10)

    # Make predictions
    predictions = model.predict(X)
    predictions = scaler.inverse_transform(
        np.hstack((predictions, np.zeros((predictions.shape[0], 2))))
    )[:, 0]

    # Plot results
    import matplotlib.pyplot as plt

    plt.figure(figsize=(16, 8))
    plt.plot(stock_data["Close"].values, label="Actual Prices")
    plt.plot(
        range(time_step + 1, len(predictions) + time_step + 1),
        predictions,
        label="Predicted Prices",
    )
    plt.xlabel("Date")
    plt.ylabel("Close Price USD ($)")
    plt.legend()
    plt.show()

    logging.info("completed")


# Main script
if __name__ == "__main__":
    logging.info("in main")
    main()
