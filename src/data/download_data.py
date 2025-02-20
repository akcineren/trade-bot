# src/data/download_data.py

import os
from binance import Client
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

def download_klines(symbol="BTCUSDT", interval="1h", lookback="1 month ago UTC"):
    """
    Default lookback is last 1 month, but you can adjust to '1 year ago UTC', etc.
    """
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    
    # Connect client (for production, set testnet=False)
    client = Client(api_key, secret_key, tld="com")
    
    # log started downloading
    logger.info(f"Downloading {symbol} {interval} klines since {lookback}")
    

    # Fetch klines
    klines = client.get_historical_klines(
        symbol,
        interval,
        lookback
    )
    # Each row in klines: 
    # [Open time, Open, High, Low, Close, Volume, Close time, ... etc. 12 columns total]
    
    logger.info(f"Downloaded {len(klines)} klines.")
    # Convert to DataFrame
    df = pd.DataFrame(
        klines, 
        columns=[
            "open_time", "open", "high", "low", "close", "volume", 
            "close_time", "quote_asset_volume", "trades", 
            "taker_base_vol", "taker_quote_vol", "ignore"
        ]
    )
    
    # Convert numeric columns from strings
    numeric_cols = ["open", "high", "low", "close", "volume", 
                    "quote_asset_volume", "taker_base_vol", "taker_quote_vol"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, axis=1)
    
    # Convert timestamps
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    
    return df

if __name__ == "__main__":
    symbol = "BTCUSDT"
    interval = "1m"
    df_klines = download_klines(symbol, interval, "1 month ago UTC")

    df_klines.to_csv(f"data_{symbol}_{interval}.csv", index=False)
    # log of finish
    logger.info(f"Saved data to data_{symbol}_{interval}.csv")
