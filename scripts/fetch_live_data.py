"""
CryptoVista - Live Market Data Fetch

This script is embedded directly inside the Power BI Power Query editor
(Crypto_Market_Live query, via a Python.Execute step) and re-runs every
time the dashboard is refreshed. It is extracted here as a standalone
file for readability and version control - to use it inside Power BI,
paste the body back into a Python script step in Power Query.

Fetches:
1. Live market data for the top 10 coins by market cap (CoinGecko API)
2. USD -> INR exchange rate (open.er-api.com), applied to produce PriceINR

Output: a pandas DataFrame loaded into Power BI as the Crypto_Market_Live table.
"""

import requests
import pandas as pd

# ===============================
# 1. Fetch live crypto prices
# ===============================
crypto_url = "https://api.coingecko.com/api/v3/coins/markets"
crypto_params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 10,
    "page": 1,
    "sparkline": "false"
}

crypto_response = requests.get(crypto_url, params=crypto_params)
crypto_data = crypto_response.json()

crypto_df = pd.DataFrame(crypto_data)[[
    "id",
    "symbol",
    "current_price",
    "market_cap",
    "total_volume",
    "price_change_percentage_24h"
]]

crypto_df.columns = [
    "Coin",
    "Symbol",
    "PriceUSD",
    "MarketCap",
    "Volume",
    "Change24h"
]

# ===============================
# 2. USD -> INR conversion
# ===============================
fx_url = "https://open.er-api.com/v6/latest/USD"
fx_data = requests.get(fx_url).json()

usd_to_inr = fx_data["rates"]["INR"]

crypto_df["PriceINR"] = crypto_df["PriceUSD"] * usd_to_inr

# ===============================
# Final output to Power BI
# ===============================
crypto_df
