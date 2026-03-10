import yfinance as yf
import pandas as pd
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

def get_macro_data():
    """Fetches key macro indicators."""
    tickers = {
        "^GSPC": "S&P 500",
        "^FTSE": "FTSE 100",
        "^BSESN": "Sensex",
        "^VIX": "VIX",
        "^TNX": "10Y Yield",
        "CL=F": "Crude Oil",
        "GC=F": "Gold"
    }
    data = []
    for ticker, name in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            data.append({"Name": name, "Price": price, "Change": change})
        except:
            pass
    return pd.DataFrame(data)

def get_stock_data(ticker_symbol):
    """Fetches comprehensive stock data."""
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    # Financials / Key Stats
    stats = {
        "Market Cap": info.get("marketCap"),
        "P/E Ratio": info.get("trailingPE"),
        "Dividend Yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
        "52W High": info.get("fiftyTwoWeekHigh"),
        "52W Low": info.get("fiftyTwoWeekLow"),
        "Volume": info.get("volume"),
        "Avg Volume": info.get("averageVolume")
    }
    
    # Key Dates
    calendar = stock.calendar
    
    # Institutional Holders
    try:
        institutional = stock.institutional_holders
        if institutional is not None:
            institutional = institutional.head(5).to_dict('records')
        else:
            institutional = []
    except:
        institutional = []
        
    return {
        "info": info,
        "stats": stats,
        "calendar": calendar,
        "institutional": institutional
    }

def get_stock_history(ticker_symbol, period="1y"):
    """Fetches historical price data for charting."""
    stock = yf.Ticker(ticker_symbol)
    return stock.history(period=period)

def get_breaking_news(query, max_results=5):
    """Fetches breaking news for a specific equity."""
    news = []
    try:
        with DDGS() as ddgs:
            results = ddgs.news(query, max_results=max_results)
            for r in results:
                news.append({
                    "title": r['title'],
                    "url": r['url'],
                    "source": r['source'],
                    "date": r['date']
                })
    except:
        pass
    return news
