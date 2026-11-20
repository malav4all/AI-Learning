import json
import math

import yfinance as yf


def get_stock_price(ticker_symbol: str) -> str:
    """Fetch the current price of a stock given its ticker symbol."""
    symbol = ticker_symbol.strip().upper()
    try:
        info = yf.Ticker(symbol).fast_info
        price = info["last_price"]
        currency = info["currency"]

        if price is None or (isinstance(price, float) and math.isnan(price)):
            return json.dumps({"ticker": symbol, "error": "No price found. The ticker may be invalid or delisted."})

        return json.dumps({
            "ticker": symbol,
            "price": round(float(price), 2),
            "currency": currency,
        })
    except Exception as e:
        print(f"Error fetching stock for {symbol}: {e}")
        return json.dumps({"ticker": symbol, "error": str(e)})


if __name__ == "__main__":
    print(get_stock_price("AAPL"))
    print(get_stock_price("ANT"))