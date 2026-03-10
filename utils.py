import yfinance as yf
import pandas as pd
import numpy as np
from duckduckgo_search import DDGS
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=600)
def get_macro_data():
    """Fetches key macro indicators with trend detection."""
    tickers = {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ",
        "^FTSE": "FTSE 100",
        "^VIX": "VIX",
        "^TNX": "10Y Yield",
        "CL=F": "Crude Oil",
        "GC=F": "Gold",
        "BTC-USD": "Bitcoin"
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

@st.cache_data(ttl=3600)
def get_advanced_stats(ticker_symbol):
    """Calculates Quantitative Health Scores (F-Score, Z-Score)."""
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        fin = stock.financials
        bs = stock.balance_sheet
        cf = stock.cashflow
        
        # Financial Health Metrics (Simplified Piotroski F-Score / Altman Z)
        # Placeholder for actual calculation logic depending on data availability
        health_score = 0
        try:
            if not fin.empty and not bs.empty:
                # F-Score checks (Simplified)
                net_income = fin.loc['Net Income'].iloc[0]
                prev_net_income = fin.loc['Net Income'].iloc[1]
                if net_income > 0: health_score += 1
                if net_income > prev_net_income: health_score += 1
                
                # Z-Score check (Simplified placeholder)
                ebit = fin.loc['EBIT'].iloc[0]
                total_assets = bs.loc['Total Assets'].iloc[0]
                if ebit / total_assets > 0.1: health_score += 1
        except:
            health_score = "N/A"
            
        return {
            "health_score": health_score,
            "insider_sentiment": info.get("heldPercentInsiders", 0) * 100,
            "short_ratio": info.get("shortRatio", 0),
            "target_mean": info.get("targetMeanPrice", 0)
        }
    except:
        return {"health_score": "N/A", "insider_sentiment": 0, "short_ratio": 0, "target_mean": 0}

@st.cache_data(ttl=1800)
def get_technical_analysis(ticker_symbol):
    """Calculates SMA, RSI, and MACD."""
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="1y")
        if df.empty: return df
        
        # SMAs
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_earnings_history(ticker_symbol):
    """Fetches Earnings surprise data with robust column mapping."""
    try:
        stock = yf.Ticker(ticker_symbol)
        earnings = stock.earnings_dates
        if earnings is not None:
            # Drop rows where we don't even have a reported or estimated value
            earnings = earnings.dropna(subset=['Reported EPS', 'EPS Estimate'], how='all')
            # Standardize columns for the app
            col_map = {
                'Reported EPS': 'Reported',
                'EPS Estimate': 'Estimate',
                'Surprise(%)': 'Surprise'
            }
            earnings = earnings.rename(columns=col_map)
            # Ensure columns exist to prevent KeyErrors
            for col in ['Reported', 'Estimate']:
                if col not in earnings.columns:
                    earnings[col] = 0
            return earnings.head(8)
        return None
    except:
        return None

@st.cache_data(ttl=3600)
def get_stock_data(ticker_symbol):
    """Enhanced stock data fetcher."""
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        stats = {
            "Market Cap": info.get("marketCap"),
            "P/E Ratio": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "Beta": info.get("beta"),
            "52W High": info.get("fiftyTwoWeekHigh"),
            "52W Low": info.get("fiftyTwoWeekLow"),
            "Volume": info.get("volume"),
            "Avg Volume": info.get("averageVolume"),
            "Currency": info.get("currency", "USD")
        }
        
        # Institutional Holders
        institutional = []
        try:
            inst_data = stock.institutional_holders
            if inst_data is not None and not inst_data.empty:
                col_map = {'Holder': 'Holder', 'Entity': 'Holder', 'Shares': 'Shares', '% Out': '% Out'}
                inst_data = inst_data.rename(columns=col_map)
                institutional = inst_data[['Holder', 'Shares', '% Out']].head(10).to_dict('records')
        except: pass
            
        return {
            "info": info,
            "stats": stats,
            "institutional": institutional,
            "calendar": stock.calendar
        }
    except Exception as e:
        return {"error": str(e), "stats": {}, "institutional": []}

@st.cache_data(ttl=3600)
def get_breaking_news(query, max_results=5):
    """Fetches breaking news."""
    news = []
    try:
        with DDGS() as ddgs:
            results = ddgs.news(query, max_results=max_results)
            for r in results:
                news.append({"title": r['title'], "url": r['url'], "source": r['source'], "date": r['date']})
    except: pass
    return news
