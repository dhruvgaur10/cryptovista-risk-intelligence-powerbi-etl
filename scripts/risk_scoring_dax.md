# CryptoVista — Risk & Sentiment Scoring (DAX)

These are calculated columns defined directly on the `Crypto_Market_Live` table in the Power BI data model (Model/Data view → column formula bar). They are **not** part of the Power Query M/Python fetch step (see `fetch_live_data.py`) — they run as DAX after the raw data loads.

## Volatility_Score

```dax
Volatility_Score =
ABS ( Crypto_Market_Live[Change24h] )
```

Absolute value of the 24h price change — direction doesn't matter, only magnitude of movement.

## Liquidity_Ratio

```dax
Liquidity_Ratio =
VAR Vol =
    VALUE ( Crypto_Market_Live[Volume] )
VAR Cap =
    VALUE ( Crypto_Market_Live[MarketCap] )
RETURN
IF (
    OR ( ISBLANK ( Vol ), ISBLANK ( Cap ) ),
    0,
    DIVIDE ( Vol, Cap )
)
```

24h trading volume divided by market cap, with a blank-safe guard (returns 0 instead of erroring if either input is missing).

## Market_Risk_Index

```dax
Market_Risk_Index =
( Crypto_Market_Live[Volatility_Score] * 0.6 ) +
( ( 1 - Crypto_Market_Live[Liquidity_Ratio] ) * 0.4 )
```

A weighted composite: 60% volatility, 40% illiquidity (`1 - Liquidity_Ratio`, so a *lower* liquidity ratio pushes risk *up*). Higher score = riskier.

## Risk_Regime

```dax
Risk_Regime =
SWITCH (
    TRUE(),
    Crypto_Market_Live[Market_Risk_Index] < 3, "Low Risk",
    Crypto_Market_Live[Market_Risk_Index] < 6, "Medium Risk",
    "High Risk"
)
```

Buckets `Market_Risk_Index` into three bands: <3 Low Risk, 3–6 Medium Risk, ≥6 High Risk. (In practice, all 10 tracked coins currently fall under 3, so only "Low Risk" appears in the live data — the Medium/High bands exist in the formula but aren't triggered at current market conditions.)

## Sentiment_Score

```dax
Sentiment_Score =
SWITCH(
    LOWER(TRIM('Crypto_Market_Live'[Symbol])),
    "btc", 0.25,
    "eth", -0.10,
    "ada", 0.05,
    "sol", 0.15,
    "xrp", -0.20,
    0.03
)
```

**This is a hardcoded lookup table by coin symbol, not a live/dynamic sentiment feed.** Each of BTC, ETH, ADA, SOL, and XRP has a manually assigned sentiment value; every other coin (including ones actually tracked, like BNB, DOGE, USDT, USDC, TRX, STETH) falls through to the default `0.03`. ADA isn't even one of the 10 coins currently tracked by the live fetch — this formula appears to predate the current coin list and was never fully updated to match it.

## Sentiment_Category

Not captured directly, but inferable from `Sentiment_Score`'s sign (matches the "Positive/Neutral/Negative" values seen in the data: BTC=0.25→Positive, ETH=-0.1→Neutral, XRP=-0.2→Negative, most others≈0.03→Neutral). Likely a `SWITCH(TRUE(), ... > threshold, "Positive", ... < threshold, "Negative", "Neutral")` pattern — exact thresholds not confirmed; re-check the formula bar for this column in Power BI Desktop if precision is needed.

## MarketCap_Log

```dax
MarketCap_Log =
IF (
    Crypto_Market_Live[MarketCap] > 0,
    LOG10 ( Crypto_Market_Live[MarketCap] ),
    BLANK()
)
```

Log10 of market cap (guarded against zero/negative input), used purely to size bubble charts sensibly across a huge range (BTC's cap vs. small-cap coins).

---

**Caveat carried over from the data itself:** `Sentiment_Score` is static/manual, not a live sentiment signal — treat "Market Sentiment" visuals on the dashboard as a fixed assumption baked into the model, not real-time market sentiment.
