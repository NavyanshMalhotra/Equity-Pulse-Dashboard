import yfinance as yf
import pandas as pd
from duckduckgo_search import DDGS
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=600) # Cache for 10 minutes
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
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((price - prev_price) / prev_price) * 100
                data.append({"Name": name, "Price": price, "Change": change})
        except:
            pass
    return pd.DataFrame(data)

@st.cache_data(ttl=3600) # Cache for 1 hour
def get_stock_data(ticker_symbol):
    """Fetches comprehensive stock data."""
    try:
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
        institutional = []
        try:
            inst_data = stock.institutional_holders
            if inst_data is not None and not inst_data.empty:
                col_map = {
                    'Holder': 'Holder', 'Entity': 'Holder', 
                    'Shares': 'Shares', 'Date Reported': 'Date', 
                    '% Out': '% Out', 'Value': 'Value'
                }
                inst_data = inst_data.rename(columns=col_map)
                for col in ['Holder', 'Shares', '% Out']:
                    if col not in inst_data.columns:
                        inst_data[col] = "N/A"
                institutional = inst_data[['Holder', 'Shares', '% Out']].head(10).to_dict('records')
        except:
            pass
            
        return {
            "info": info,
            "stats": stats,
            "calendar": calendar,
            "institutional": institutional
        }
    except Exception as e:
        return {"error": str(e), "stats": {}, "institutional": [], "calendar": None}

@st.cache_data(ttl=1800) # Cache for 30 mins
def get_stock_history(ticker_symbol, period="1y"):
    """Fetches historical price data for charting."""
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.history(period=period)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache news for 1 hour
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
